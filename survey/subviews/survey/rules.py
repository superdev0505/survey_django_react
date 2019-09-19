import logging
import random
import traceback
from datetime import timedelta

from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone

from django_server.db import fetch_all
from django_server.settings import SURVEY_DEFAULT_QUESTION_TIMEOUT
from survey.models import IPHistory
from survey.submodels.fingerprint import UserFingerprint
from survey.submodels.survey import Question

logger = logging.getLogger(__name__)


MINUTE = 60
MINUTES_15 = 15 * 60
HOURS_24 = 24 * 60 * 60
DAYS_7 = 7 * 24 * 60 * 60

# Some questions will be repeated, to check if user is tricky
REPEATED_QUESTIONS = [6, 18, 27, 38, 43, 56]

# If user pass 50% of repeated questions with different answers (wrong answers),
# survey wont be passed
SURVEY_PASS_THRESHOLD = 1 # (SURVEY_DEFAULT_QUESTION_COUNT/ len(REPEATED_QUESTIONS)) / 2

# If user's IP changed, how many times he can change it during the day
USER_CAN_CHANGE_IP_PER_DAY = 10

# Percentage rate of how often Antibot question will appear
BOT_QUESTION_APPEAR_RATE = 0.6

# Count of survey in a row that user can do
ZOMBIE_QUESTION_COUNT = 140

# TOTAL_QUESTIONS = Question.objects.count()

SURVEY_BOT_QUESTION = 'SURVEY_BOT_QUESTION'
SURVEY_USER_SOLVED_QUESTIONS = 'SURVEY_USER_SOLVED_QUESTIONS'


##
# Main logic for selecting question
#
def select_question(survey, previous_answer_tags=None):
    user_id = str(survey.user.id)

    # Repeated questions
    # questions_count = survey.questionanswer_set.count()
    # if questions_count in REPEATED_QUESTIONS:
    #     possible_questions = survey.questionanswer_set.all().order_by('id')
    #     rq = REPEATED_QUESTIONS
    #     index_to = rq.index(questions_count)
    #     position_to = rq[index_to]
    #     position_from = rq[rq.index(questions_count) - 1] + 1 if index_to > 0 else 0
    #     return random.choice(possible_questions[position_from:position_to]).question

    # Ever answered questions
    user_solved_questions_id = cache.get(SURVEY_USER_SOLVED_QUESTIONS + user_id) or []

    question = do_select_question(survey, user_id, user_solved_questions_id, previous_answer_tags=previous_answer_tags)
    update_available_questions(user_id, user_solved_questions_id, question)
    survey.current_question = question
    return question


def do_select_question(survey, user_id,  user_solved_questions_id, previous_answer_tags=None):

    # Check if user already passed ANTIBOT question
    # questions_count = survey.questionanswer_set.count()
    # passed_bot_question = cache.get(SURVEY_BOT_QUESTION + str(survey.id))
    # if hasattr(survey.user, 'provider') and (not passed_bot_question) and (questions_count > 3) and (random.random() > BOT_QUESTION_APPEAR_RATE):
    #     logger.info('[BOT Question] {} - {} - {}'.format(SURVEY_BOT_QUESTION + user_id, survey.user, passed_bot_question))
    #     question = Question.objects.all().exclude(enabled=False).filter(tags__text=BOT_QUESTION_TAG).filter(~Q(id__in=user_solved_questions_id)).first()
    #     if question:
    #         logger.info('[BOT Question] SET {} - {} - q: {}'.format(SURVEY_BOT_QUESTION + user_id, survey.user, question.id))
    #         cache.set(SURVEY_BOT_QUESTION + str(survey.id), question.id, timeout=MINUTE)
    #         return question

    # available non bot and not answered questions
    available_questions = Question.objects.exclude(enabled=False).exclude(tags__text=BOT_QUESTION_TAG).filter(~Q(id__in=user_solved_questions_id))

    # If previous answer contained some tag
    if previous_answer_tags and len(previous_answer_tags):
        tagged_questions = available_questions.filter(tags__text__in=previous_answer_tags)
        if len(tagged_questions):
            return random.choice(tagged_questions)

    # By default using random choice
    if len(available_questions) > 0:
        return random.choice(available_questions)
    else:
        return random.choice(Question.objects.filter(enabled=True))


def update_available_questions(user_id, user_solved_questions, question):
    user_solved_questions.append(question.id)
    cache.set(SURVEY_USER_SOLVED_QUESTIONS + user_id, user_solved_questions, timeout=DAYS_7)


##
# Below logic of checking answers
#

# Allow only 3 IP changed per 24 hour
def is_often_changed_ip(survey, ip):
    delta_24h = timezone.now() - timedelta(hours=24)

    ip_exist = IPHistory.objects.filter(user=survey.user, ip=ip).order_by('-date').first()
    if not ip_exist:
        IPHistory.objects.create(user=survey.user, ip=ip)

    return IPHistory.objects.filter(user=survey.user, date__gt=delta_24h).count() > USER_CAN_CHANGE_IP_PER_DAY


# Check if someone using same IP TODO
def is_using_same_ip(survey, ip):
    delta_1h = timezone.now() - timedelta(minutes=30)

    same_ip_usage_count = IPHistory.objects.exclude(user=survey.user).filter(ip=ip, date__gt=delta_1h).count()
    if same_ip_usage_count:
        logger.info('[SAME IP DETECTED] someone using {} same ips {} as user {}'.format(same_ip_usage_count, ip, survey.user))
        if same_ip_usage_count > 1:
            return True

    return False


# Check if user coming with same fingerprint as other user
def is_same_fingerprint(survey):
    delta_1h = timezone.now() - timedelta(hours=24)

    try:
        same_fingerprint = UserFingerprint.objects.exclude(user=survey.user).filter(user__provider=survey.user.provider).filter(fingerprint__id__in=UserFingerprint.objects.filter(user=survey.user).values_list('fingerprint_id', flat=True), date__gte=delta_1h)
        if same_fingerprint.count() > 5:
            logger.info('[SAME FINGERPRINT DETECTED] someone using same fp {} as user {} - {} - {}'.format(same_fingerprint.first().id, survey.user, survey.user.provider, survey.user.id))
            return True
    except Exception as e:
        logger.error('[SAME FINGERPRINT DETECTED] {}'.format(e))
        traceback.print_exc()

    logger.info('[SAME FINGERPRINT] same Not found {} - {} - {}'.format(survey.user, survey.user.provider, survey.user.id))

    return False


# If user don't have any fingerprint
def has_no_fingerprint(survey):
    user = survey.user
    key = 'NO_FINGERPRINT_{}'.format(user.id)

    if not cache.get(key) and user.survey_set.count() > 4:
        if not survey.user.fingerprint.all().count():
            cache.set(key, 'no_fingerprint')
            return True
        else:
            cache.set(key, 'fingerprint')


# If user somehow solved survey quicker than minimum time of survey
def is_quick_solve_survey(survey):
    delta_min_survey_timeout = timezone.now() - timedelta(seconds=survey.user.provider.question_count * SURVEY_DEFAULT_QUESTION_TIMEOUT)
    return survey.created > delta_min_survey_timeout


BOT_QUESTION_TAG = 'bot'
BOT_ANSWER_TAG = 'passed bot test'
# If user not solved "Antibot questions"
def is_bot(survey):
    qa = survey.questionanswer_set.filter(question__tags__text=BOT_QUESTION_TAG).first()
    if qa:
        return qa.choice.filter(tags__text=BOT_ANSWER_TAG).first() is None
    return False


# If user like a zombie solving one by one
def is_zombie(survey):
    return survey.user.survey_set.filter(created__gte=timezone.now() - timedelta(hours=4)).count() > ZOMBIE_QUESTION_COUNT

    # if user still solving 16 hours in 24 hours


def is_zombie_16h(survey):
    sql_16h = '''
        select TO_CHAR(created, 'yyyy-mm-dd HH24') as trdate, count(*) cnt 
          from survey_survey 
          where created > current_date -1 and user_id=%s 
          group by trdate 
          order by trdate desc;
    '''

    if len(fetch_all(sql_16h, [survey.user.id])) >= 16:
        return True


# If user randomly answer questions without any logic
def is_contradicting_answers(survey):
    answers = fetch_all('''
        with
          data as(
              select qa.id, qa.question_id, sum(qac.choice_id)
              from survey_questionanswer qa
              full outer join survey_questionanswer_choice qac on qac.questionanswer_id = qa.id
              where survey_id = %s
              group by qa.id, qa.question_id
          ),
          uniq_answers as (
              select distinct question_id, sum
              from data
              GROUP BY question_id, sum
            )
        select question_id, count(*)
        from uniq_answers
        group by question_id
        HAVING count(*) > 1;
    ''', [survey.id])
    if answers and len(answers):
        logger.info('[CONTRADICTING] user {} has {} contr questions'.format(survey.user, len(answers)))
        return len(answers) >= SURVEY_PASS_THRESHOLD
    else:
        return False