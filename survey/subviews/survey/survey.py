import logging
import random
import traceback
from datetime import timedelta

from django import urls
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import timezone
from googletrans import Translator
from django.db.models import Count

from django_server import db
from django_server.settings import SURVEY_DEFAULT_QUESTION_TIMEOUT
from django_server.utils import get_client_ip, is_mobile
from survey.models import UserFlags, UserBanHistory
from survey.submodels.article import Article
from survey.submodels.survey import Survey, ANSWER_TEXT, ANSWER_VOTE, Choice, ANSWER_RADIO, \
    SURVEY_STATUS_HAS_CONTRADICTING, SURVEY_STATUS_CHANGED_IP, \
    SURVEY_STATUS_SOLVE_TOO_QUICK, SURVEY_STATUS_ZOMBIE, SURVEY_STATUS_BOT, SURVEY_STATUS_SUCCESS, QuestionAnswer, \
    DEVICE_DESKTOP, DEVICE_MOBILE
from survey.submodels.transaction import Transaction
from survey.subviews import auth
from survey.subviews.proof import try_set_proof
from survey.subviews.survey import rules
from survey.subviews.auth import get_user, do_login

logger = logging.getLogger(__name__)

translator = Translator()


def article(request, article=None):
    current_language = request.session.get('selected_language')
    if not current_language:
        current_language = 'EN'

    if article:
        article = Article.objects.filter(url=article, enabled=True).first()
        if article:
            article.title = translator.translate(article.title, dest=current_language.lower()).text
            # article.text = translator.translate(article.text, dest=current_language.lower()).text
            return get_survey(request, article=article)
    article = Article.get_article()
    return redirect('/article/' + article.url)


def survey(request):
    ref_id = request.GET.get('ref_id')

    user = request.user
    if ref_id:
        try:
            user = get_user(request, ref_id)
            do_login(request, user)
        except Exception as e:
            redirect('/')

    article = Article.get_article()
    return redirect('/article/' + article.url)


def get_survey(request, article=None):
    context = {}
    question = None
    user = request.user
    user_ip = get_client_ip(request)
    user_is_mobile = is_mobile(request)

    current_language = request.session.get('selected_language')
    if not current_language:
        current_language = 'EN'

    if request.user.is_anonymous:
        user = auth.get_user(request)
        user = auth.do_login(request, user)

    # if request.user.ref_id and request.user.social_auth.count() == 0:
    #     return redirect('/#social_auth_required')

    survey = Survey.get_current_survey(user)
    solved_questions_count = 0

    if not survey:
        survey, question = Survey.get_survey(user)
    else:
        progress, solved_questions_count = survey.progress
        if progress >= 100:
            if hasattr(user, 'provider'):
                solved = try_solve_survey(survey, user, user_ip, context)
                survey.solved = timezone.now()
                survey.device = DEVICE_MOBILE if user_is_mobile else DEVICE_DESKTOP
                survey.save()

                # For now pay only to mobile Users
                if solved:
                    logger.info('[Survey] success survey - {} - {} - {} - {}'.format(survey.id, survey, user, user.provider))
                    Transaction.do_payout(survey, user_is_mobile, user_ip)
                context['all_answered'] = True
            else:
                context['all_answered'] = True
                survey.solved = timezone.now()
                survey.save()
                return render(request, 'survey/survey.html', context)

            context['show_feedback'] = try_show_feedback(user)
        else:
            question = survey.current_question
            if not question:
                question = rules.select_question(survey)
                survey.add_question(question)

        context['progress'] = int(progress)
        # security actions below
        context['proof_sign'] = try_set_proof(user, survey)

    if not survey.solved:
        question.text = translator.translate(question.text, dest=current_language.lower()).text
        context['question'] = question
        if question.answer_type == ANSWER_VOTE:
            choices = list(question.choice_set.all())
            random.shuffle(choices)
            choice_1 = choices[0]
            choice_1.text = translator.translate(choice_1.text, dest=current_language.lower()).text
            context['choice1'] = choice_1
            context['choice1_count'] = choice_1.get_answers_count()
            choice_2 = choices[1]
            choice_2.text = translator.translate(choice_2.text, dest=current_language.lower()).text
            context['choice2'] = choice_2
            context['choice2_count'] = choice_2.get_answers_count()
        else:
            choices = list(question.choice_set.all())
            # for choice in choices:
                # choice.text = translator.translate(choice.text, dest=current_language.lower()).text
            random.shuffle(choices)
            context['choices'] = choices

    if not article:
        article = Article.get_article(solved_questions_count)

    context['article'] = article
    context['timer'] = SURVEY_DEFAULT_QUESTION_TIMEOUT
    context['all_questions'] = user.provider.question_count if hasattr(survey.user, 'provider') else 10
    context['solved_questions'] = solved_questions_count

    return render(request, 'survey/survey.html', context)


##
# Finally solve survey
#
def vote(request):
    if request.method != 'POST':
        return redirect('/')

    user = request.user
    survey = Survey.get_current_survey(user)

    if not survey:
        return redirect('/')

    question = survey.current_question
    answer = survey.get_current_answer()

    if not question:
        return redirect('/')

    if question.answer_type == ANSWER_TEXT:
        choice,created = Choice.objects.get_or_create(question=question, text=request.POST.get('choice'))
        choice.save()
        selected_choices = [choice]
    elif question.answer_type == ANSWER_RADIO:
        selected_choices = [question.choice_set.filter(pk=request.POST.get('choice')).first()]
    elif question.answer_type == ANSWER_VOTE:
        selected_choices = [question.choice_set.filter(pk=request.POST.get('choice')).first()]
    else:
        selected_choices = []
        for choice in request.POST.getlist('choice'):
            try:
                selected_choices.append(int(choice))
            except Exception as e:
                logger.error('[Survey] vote - {}'.format(e))
        selected_choices = list(question.choice_set.filter(pk__in=selected_choices))
        if len(selected_choices) > 33:
            return redirect(urls.reverse('survey:survey') + '#error=survey_many_answers')

    try:
        survey.answer_question(question, selected_choices, answer=answer)
    except Exception as e:
        logger.error(e)
        traceback.print_exc()
        return redirect(urls.reverse('survey:survey'))

    # Update User own tags
    answer_tags = []
    for choice in selected_choices:
        answer_tags.extend(list(choice.tags.values_list('text', flat=True)))
    user.add_tags(answer_tags)

    # Select next question
    progress, solved = survey.progress
    if progress < 100:
        survey.add_question(rules.select_question(survey, previous_answer_tags=answer_tags))

    next_article = Article.get_next_article(current_index=solved)
    redirect_url = '/article/' + next_article.url
    return HttpResponseRedirect(redirect_url)


##
# Main antifraud strategy
# survey - Mutable
# context - Mutable
#
def try_solve_survey(survey, user, ip, context):

    # if rules.is_using_same_ip(survey, ip):
    #     UserFlags.objects.create(user=user, key=UserFlags.SAMEIP)
    #     UserBanHistory.block_user(user, 60, 'Same IP detected')

    if rules.is_same_fingerprint(survey):
        logger.warning('[Survey] SAME FINGERPRING FOUND - {} - {} - {}'.format(survey.id, survey, survey.user))
        UserFlags.objects.create(user=user, key=UserFlags.SAMEFGPT)
        context['survey_error'] = 'Your behaviour is looking suspicious'
        survey.status = SURVEY_STATUS_BOT
        UserBanHistory.block_user(user, 9999, 'SAME fingerprint found')
        user.is_active = False
        user.save()
        return False

    if rules.has_no_fingerprint(survey):
        logger.warning('[Survey] has_no_fingerprint in survey - {} - {} - {}'.format(survey.id, survey, survey.user))
        context['survey_error'] = 'Your behaviour is looking suspicious'
        UserFlags.objects.create(user=user, key=UserFlags.NO_FGPT)
        survey.status = SURVEY_STATUS_BOT
        UserBanHistory.block_user(user, 9999, 'No fingerprint found')
        user.is_active = False
        user.save()
        return False

    # if rules.is_contradicting_answers(survey):
    #     logger.info('[Survey] has_contradicting in survey - {} - {} - {}'.format(survey.id, survey, survey.user))
    #     context['survey_error'] = 'Your survey was found invalid because You gave contradictory answers. 1 of the 10 questions is repeated and you must provide the same answer. Contradicting answers result in invalid survey. Try again and pay closer attention.'
    #     UserFlags.objects.create(user=user, key=UserFlags.CONTRADC)
    #     survey.status = SURVEY_STATUS_HAS_CONTRADICTING
    #     return False

    if rules.is_often_changed_ip(survey, ip):
        logger.info('[Survey] is_often_changed_ip in survey - {} - {} - {}'.format(survey.id, survey, survey.user))
        context['survey_error'] = 'Your IP changed too many times. You must wait 24 hours before using our site again.'
        UserFlags.objects.create(user=user, key=UserFlags.OFTNIP)
        survey.status = SURVEY_STATUS_CHANGED_IP
        return False

    # if rules.is_bot(survey):
    #     logger.info('[Survey] is_bot in survey - {} - {} - {}'.format(survey.id, survey, survey.user))
    #     context['survey_error'] = 'Your survey was found invalid because you answered incorrectly an "Attention Checker" detection question. Pay closer attention to your answers next time. Please try again.'
    #     UserFlags.objects.create(user=user, key=UserFlags.BOT)
    #     survey.status = SURVEY_STATUS_BOT
    #     suspend_user(survey.user)
    #     return False

    # if rules.is_zombie(survey):
    #     logger.warning('[Survey] is_zombie in survey - {} - {} - {}'.format(survey.id, survey, survey.user))
    #     context['survey_error'] = 'Take a break. You have been answering surveys for 4 hours straight. You may resume in 4 hours.'
    #     UserFlags.objects.create(user=user, key=UserFlags.ZOMBIE)
    #     survey.status = SURVEY_STATUS_ZOMBIE
    #     suspend_user(survey.user)
    #     return False

    # if rules.is_zombie_16h(survey):
    #     logger.warning('[Survey] is_zombie in survey - {} - {} - {}'.format(survey.id, survey, survey.user))
    #     context['survey_error'] = 'Take a break. You have been answering surveys for a long time! You may resume in 24 hours.'
    #     UserFlags.objects.create(user=user, key=UserFlags.ZOMBIE)
    #     survey.status = SURVEY_STATUS_ZOMBIE
    #     UserBanHistory.block_user(user, 24 * 60, 'zombie - 16h in a row')
    #     return False

    if rules.is_quick_solve_survey(survey):
        logger.info('[Survey] is_quick_solve_survey - {} - {} - {}'.format(survey.id, survey, survey.user))
        context['survey_error'] = 'Your behaviour is looking suspicious, You are solving questions too quick'
        UserFlags.objects.create(user=user, key=UserFlags.OFTNSOLV)
        survey.status = SURVEY_STATUS_SOLVE_TOO_QUICK
        return False

    survey.status = SURVEY_STATUS_SUCCESS
    return True


BLOCK_USER_AFTER_FAILS = 10
SUSPEND_MAP = [0, 15, 30, 45, 60, 2*60, 3*60, 4*60, 5*60, 8*60]
def suspend_user(user):
    fails_count = Survey.objects.filter(
        user=user,
        created__gte=timezone.now()-timedelta(days=2),
        status__in=[SURVEY_STATUS_ZOMBIE, SURVEY_STATUS_BOT]).count()

    if fails_count:
        if fails_count > 10:
            logger.info('[BLOCK USER] user {} - {} was blocked because of {} fails'.format(user, user.ref_id, fails_count))
            UserBanHistory.block_user(user, 7 * 24 * 60 * 60, 'Fails count {}'.format(fails_count))
            return

        if fails_count > 1:
            logger.info('[SUSPEND USER] user {} - {} was blocked because of {} fails'.format(user, user.ref_id, fails_count))
            block_timeout = SUSPEND_MAP[fails_count]
            UserBanHistory.block_user(user, block_timeout, 'Fails count {}'.format(fails_count))


# Shows feedback form on 3rd survey ends
def try_show_feedback(user):
    return user.survey_set.all().count() == 3