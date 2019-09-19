from django.db.models import *
from django.utils import timezone
from django.core.cache import cache

from django_server import db
from django_server.db import LONG_STRING_LENGTH, SHORT_STRING_LENGTH, DEFAULT_STRING_LENGTH
from django_server.settings import DAYS_7
from survey.models import SurveyUser
from survey.submodels.tag import Tag

HOURS_24 = 24 * 60 * 60

CURRENT_USER_SURVEY_KEY = 'CURRENT_USER_SURVEY_KEY'


DEVICE_MOBILE = 0
DEVICE_DESKTOP = 1
DEVICE_TYPES = [
    (DEVICE_MOBILE, DEVICE_MOBILE),
    (DEVICE_DESKTOP, DEVICE_DESKTOP),
]


ANSWER_VOTE = 'vote'
ANSWER_TEXT = 'textarea'
ANSWER_RADIO = 'radio'
ANSWER_CHECKBOX = 'checkbox'
ANSWER_TYPES = [
    (ANSWER_VOTE, ANSWER_VOTE),
    (ANSWER_TEXT, ANSWER_TEXT),
    (ANSWER_RADIO, ANSWER_RADIO),
    (ANSWER_CHECKBOX, ANSWER_CHECKBOX)
]


class Question(Model):
    thumbnail = FileField(upload_to='question_images', default='', blank=False, null=False)
    text = CharField(max_length=LONG_STRING_LENGTH)
    answer_type = CharField(choices=ANSWER_TYPES, default=ANSWER_RADIO, blank=False, max_length=SHORT_STRING_LENGTH)
    tags = ManyToManyField(Tag)
    enabled = BooleanField(default=False)

    def __str__(self):
        return self.text

    def get_tags(self):
        return ' - '.join(str(x) for x in self.tags.all())


class Choice(Model):
    question = ForeignKey(Question, on_delete=CASCADE)
    text = CharField(max_length=DEFAULT_STRING_LENGTH)
    tags = ManyToManyField(Tag)

    CACHE_KEY = 'CHOICE_COUNT_{}'

    class Meta:
        indexes = [
            Index(fields=['id']),
        ]

    def __str__(self):
        return self.text

    def get_answers_count(self):
        return cache.get(self.CACHE_KEY.format(self.id)) or 0

    def increase_answers_count(self):
        count = cache.get(Choice.CACHE_KEY.format(self.id))
        cache.set(Choice.CACHE_KEY.format(self.id), count + 1, timeout=DAYS_7)

    @staticmethod
    def refresh_cache():
        # Update cache of all answers counters
        sql = 'select choice_id, count(*) from survey_questionanswer_choice group by choice_id'
        for q in db.fetch_all(sql):
            cache.set(Choice.CACHE_KEY.format(q.get('choice_id')), q.get('count'), timeout=DAYS_7)

Choice.refresh_cache()


SURVEY_STATUS_NEW = 0
SURVEY_STATUS_SUCCESS = 1
SURVEY_STATUS_HAS_CONTRADICTING = 2
SURVEY_STATUS_CHANGED_IP = 3
SURVEY_STATUS_SOLVE_TOO_QUICK = 4
SURVEY_STATUS_ZOMBIE = 5
SURVEY_STATUS_BOT = 6
SURVEY_STATUS = [
    ('new', SURVEY_STATUS_NEW),
    ('success', SURVEY_STATUS_SUCCESS),
    ('has_contradicting', SURVEY_STATUS_HAS_CONTRADICTING),
    ('changed_ip', SURVEY_STATUS_CHANGED_IP), # Case if looks like a bot that changed ip during survey resolving
    ('solve_too_often', SURVEY_STATUS_SOLVE_TOO_QUICK), # User solved survey too quick, less then in 10 minutes
    ('zombie', SURVEY_STATUS_ZOMBIE), # Case if user solved surveys to many in a day 24/7 solving?
    ('bot', SURVEY_STATUS_BOT), # Case if user solved survey with wrong answer in "antibot" question?
]


class Survey(Model):
    created = DateTimeField(default=timezone.now)
    user = ForeignKey(SurveyUser, on_delete=CASCADE, null=True, blank=True)
    solved = DateTimeField(null=True, blank=True)
    current_question = ForeignKey(Question, on_delete=CASCADE, null=True, blank=True)
    status = IntegerField(choices=SURVEY_STATUS, default=SURVEY_STATUS_NEW)
    device = IntegerField(choices=DEVICE_TYPES, default=DEVICE_DESKTOP)

    class Meta:
        indexes = [
            Index(fields=['user']),
            Index(fields=['solved', 'user']),
            Index(fields=['user', 'solved']),
            Index(fields=['id']),
        ]

    def __str__(self):
        return '{} - {}'.format(self.user, self.created)

    @property
    def progress(self):
        solved = self.questionanswer_set.filter(choice__isnull=False).distinct().count()
        count = self.user.provider.question_count if hasattr(self.user, 'provider') else 10
        return (solved / count) * 100, solved

    @classmethod
    def get_current_survey(cls, user):
        key = CURRENT_USER_SURVEY_KEY + str(user.id)
        survey_id = cache.get(key)
        survey = None

        if survey_id:
            survey = cls.objects.filter(id=survey_id).first()
            if survey.solved:
                survey = None

        if not survey:
            survey = cls.objects.filter(user=user, solved__isnull=True).first()
            if survey:
                cache.set(key, survey.id, timeout=HOURS_24)
        return survey

    def get_current_answer(self):
        return self.questionanswer_set.filter(choice__isnull=True).order_by('-id').first()

    def get_solved_questions(self):
        return self.questionanswer_set.exclude(choice__isnull=True)

    def add_question(self, question):
        QuestionAnswer.objects.create(question=question, survey=self)
        self.current_question = question
        self.save()

    def answer_question(self, question, choices, answer=None):
        if not answer:
            answer = QuestionAnswer.objects.filter(question=question, survey=self).order_by('-id').first()
        answer.choice.set(choices)

        # Update cache of current answer counters
        for choice in choices:
            Choice.increase_answers_count(choice)

    ##
    # Generate next survey
    #
    def get_survey(user):
        from survey.subviews.survey import rules
        survey = Survey.objects.create(user=user)
        question = rules.select_question(survey)
        survey.add_question(question)
        return survey, question


class QuestionAnswer(Model):
    survey = ForeignKey(Survey, on_delete=CASCADE)
    question = ForeignKey(Question, on_delete=CASCADE, blank=True, null=True)
    choice = ManyToManyField(Choice)
    created = DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            Index(fields=['question', 'survey']),
        ]

    def __str__(self):
        return '{} -> {}'.format(self.question.text, list(self.choice.values()))

    def get_answers(self):
        return ' - '.join(str(x) for x in self.choice.all())
