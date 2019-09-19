import logging
import random
from time import sleep

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from django_server.settings import SURVEY_DEFAULT_QUESTION_TIMEOUT
from survey.models import SurveyUser, IPHistory, RefIdHistory
from survey.submodels.provider import Provider, PAYOUT_USER_BITCOIN
from survey.submodels.survey import Choice, ANSWER_TEXT, ANSWER_RADIO, SURVEY_STATUS, Survey
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


def create_user_and_run(provider):

    if not provider:
        # Create Provider
        provider, created = Provider.objects.get_or_create(name=PROVIDER_NAME)
        if created:
            provider.payout_method = PAYOUT_USER_BITCOIN
            provider.save()

    # Clear previous tests
    SurveyUser.objects.filter(provider__name=provider.name, provider_user_id=PROVIDER_USER_ID).delete()
    Choice.objects.filter(text=TEXT_CHOICE_NAME).delete()

    # Create referrer
    ref = RefIdHistory.get_or_create_reference(provider, PROVIDER_USER_ID)

    # Bind user to created referrer
    user = get_user(None, ref_id=ref.id)
    user.update_data({
        'bitcoin_address': USER_BTC
    })

    # Case normal
    logger.info('__________________________')
    logger.info('[Case] normal')
    run_test(user, contradicting=False)


def run_test(user, contradicting=False, user_ip=DEFAULT_USER_IP, is_bot=False, is_quick=False, is_mobile=False):
    survey, question = Survey.get_survey(user)

    print('[Survey] {} \n'.format(question))

    while survey.progress[0] < 100:

        if not is_quick:
            sleep(SURVEY_DEFAULT_QUESTION_TIMEOUT)

        question = survey.current_question
        print('[Question] {} -- {}'.format(question, [t for t in question.tags.values_list('text', flat=True)]))

        choices = get_choices(survey, question, contradicting=contradicting, is_bot=is_bot)
        print('[Choices] {} -- {} \n'.format([c.text for c in choices], [[t for t in c.tags.all()] for c in choices]))

        try_solve_question(survey, question, choices)

    solved = try_solve_survey(survey, user, user_ip, {})

    if solved:
        print('[Survey] success survey - {} - {} - {}'.format(survey.id, survey, user))
        Transaction.do_payout(survey, is_mobile, user_ip)

    survey.solved = timezone.now()
    survey.save()

    print('[Solved] {}'.format(solved))


def get_choices(survey, question, contradicting=False, is_bot=False):
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
    else:
        return secure_random.choices(question.choice_set.all())


def try_solve_question(survey, question, choices):
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