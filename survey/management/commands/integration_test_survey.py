import logging
import random
from time import sleep

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from django_server.settings import SURVEY_DEFAULT_QUESTION_TIMEOUT
from survey.models import SurveyUser, IPHistory, RefIdHistory
from survey.submodels.provider import Provider, PAYOUT_USER_BITCOIN, PAYOUT_PROVIDER_BITCOIN
from survey.submodels.survey import Choice, ANSWER_TEXT, ANSWER_RADIO, SURVEY_STATUS, Survey, ANSWER_VOTE
from survey.submodels.transaction import Transaction
from survey.subviews.auth import get_user
from survey.subviews.survey import rules
from survey.subviews.survey.rules import select_question, REPEATED_QUESTIONS, BOT_QUESTION_TAG, BOT_ANSWER_TAG
from survey.subviews.survey.survey import try_solve_survey

logger = logging.getLogger(__name__)

secure_random = random.SystemRandom()

DEFAULT_USER_IP = '1.1.1.1'
TEXT_CHOICE_NAME = 'integration_test_survey'
PROVIDER_NAME = 'test'
PROVIDER_USER_ID = 'integration_test_survey'
USER_BTC = '35HSvtrUE8wj368Sua7BsBanqvtSdMM9gL'


class Command(BaseCommand):
    help = 'Run integration test of creating survey and passing it with different conditions'

    def add_arguments(self, parser):
        parser.add_argument('-p', help='Provider name',)
        parser.add_argument('-u', help='Provider user id',)
        parser.add_argument('-b', help='BTC Address',)
        parser.add_argument('-ip', help='User IP',)
        parser.add_argument('-s', help='Send Faucethub',)

    def handle(self, *args, **options):

        bitcoin_address = options.get('b') or USER_BTC
        user_ip = options.get('ip') or DEFAULT_USER_IP

        # Get or Create Provider
        if options['p']:
            provider = Provider.objects.filter(name=options['p']).first()
            if not provider:
                logger.error('Wrong provider given')
                return
        else:
            provider, created = Provider.objects.get_or_create(name=PROVIDER_NAME)
            if created:
                provider.payout_method = PAYOUT_USER_BITCOIN
                provider.save()

        # Get or Create User
        if options['u']:
            logger.info(options)
            user = SurveyUser.objects.filter(provider=provider, provider_user_id=options['u']).first()
            if not user:
                logger.error('Wrong USER given')
                return
        else:
            # Clear previous tests
            SurveyUser.objects.filter(provider__name=provider.name, provider_user_id=PROVIDER_USER_ID).delete()
            Choice.objects.filter(text=TEXT_CHOICE_NAME).delete()

            # Create referrer
            ref = RefIdHistory.get_or_create_reference(provider, PROVIDER_USER_ID)

            if not ref.bitcoin_address and ref.provider.payout_method in [PAYOUT_USER_BITCOIN, PAYOUT_PROVIDER_BITCOIN]:
                ref.bitcoin_address = bitcoin_address
                ref.save()

            # Bind user to created referrer
            user = get_user(None, ref_id=ref.id)
            user.country = 'US'
            user.save()
            user.update_data({
                'country': 'US',
                'bitcoin_address': bitcoin_address
            })

        logger.info('Provider: {}'.format(provider))
        logger.info('User: {}'.format(user))

        # send_payout = options.get('s')
        # if send_payout:
        #     send_payout = False
        send_payout = True
        ##
        # Survey logic starts -->
        #

        # Case user selected contradicting
        # logger.info('__________________________')
        # logger.info('[Case] user is bot')
        # self.run_survey(user, is_bot=True)

        # Case normal
        logger.info('__________________________')
        logger.info('[Case] normal')
        self.run_survey(user, user_ip=user_ip, contradicting=False, send_payout=send_payout, is_mobile=True)

        # # Case is_quick_solve_survey
        # logger.info('__________________________')
        # logger.info('[Case] is_quick_solve_survey')
        # self.run_survey(user, is_quick=True)
        #
        # # Case user selected contradicting
        # logger.info('__________________________')
        # logger.info('[Case] user selected contradicting')
        # self.run_survey(user, contradicting=True)
        #
        # # Case user changed ip
        # logger.info('__________________________')
        # logger.info('[Case] user changed ip')
        # IPHistory.objects.create(user=user, ip='2.2.2.2')
        # IPHistory.objects.create(user=user, ip='3.3.3.3')
        # self.run_survey(user, user_ip='4.4.4.4')

        logger.info('--')
        logger.info('[Final Survey] -- {}'.format([SURVEY_STATUS[s.status] for s in user.survey_set.all()]))
        logger.info('[Final Tags]   -- {}'.format(user.tags))
        logger.info('[Final Flags]  -- {}'.format([k.key for k in user.user_flags.all()]))

    def run_survey(self, user, contradicting=False, user_ip=DEFAULT_USER_IP, is_bot=False, is_quick=False, is_mobile=False, send_payout=True):
        survey, question = Survey.get_survey(user)
        logger.info('[Survey] {} \n'.format(question))

        while survey.progress[0] < 100:

            if not is_quick:
                sleep(SURVEY_DEFAULT_QUESTION_TIMEOUT)

            question = survey.current_question
            logger.info('[Question] {} {} -- {}'.format(question.id, question, [t for t in question.tags.values_list('text', flat=True)]))

            choices = self.get_choices(survey, question, contradicting=contradicting, is_bot=is_bot)
            logger.info('[Choices] {} -- {} \n'.format([c.text for c in choices], [[t for t in c.tags.all()] for c in choices]))

            self.try_solve_question(survey, question, choices)

        solved = try_solve_survey(survey, user, user_ip, {})

        if solved:
            logger.info('[Survey] success survey - {} - {} - {}'.format(survey.id, survey, user))
            if send_payout:
                Transaction.do_payout(survey, is_mobile, user_ip)

        survey.solved = timezone.now()
        survey.save()

        logger.info('[Solved] {}'.format(solved))


    def get_choices(self, survey, question, contradicting=False, is_bot=False):
        if not contradicting:
            questions_count = survey.questionanswer_set.count()
            if questions_count - 1 in REPEATED_QUESTIONS:
                return list(survey.questionanswer_set.filter(question__id=question.id).first().choice.all())

        is_bot_question = question.tags.filter(text=BOT_QUESTION_TAG).first()
        if is_bot_question:
            if is_bot:
                return survey.get_current_answer().question.choice_set.exclude(tags__text=BOT_ANSWER_TAG)
            else:
                return survey.get_current_answer().question.choice_set.filter(tags__text=BOT_ANSWER_TAG)

        if question.answer_type == ANSWER_TEXT:
            choice,created = Choice.objects.get_or_create(question=question, text=TEXT_CHOICE_NAME)
            choice.save()
            return [choice]
        elif question.answer_type == ANSWER_RADIO:
            return [secure_random.choice(question.choice_set.all())]
        elif question.answer_type == ANSWER_VOTE:
            return [secure_random.choice(question.choice_set.all())]
        else:
            return secure_random.choices(question.choice_set.all())


    def try_solve_question(self, survey, question, choices):
        survey.answer_question(question, choices)

        # Update User own tags
        answer_tags = []
        for choice in choices:
            answer_tags.extend(list(choice.tags.values_list('text', flat=True)))
        survey.user.add_tags(answer_tags)

        # Select next question
        progress, solved = survey.progress
        if progress < 100:
            survey.add_question(rules.select_question(survey, previous_answer_tags=answer_tags))