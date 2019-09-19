import csv
import random

from django.core.management.base import BaseCommand

from survey.admin_views import do_question_save
from survey.submodels.survey import ANSWER_VOTE, Question
from survey.subviews.survey.rules import BOT_QUESTION_TAG, BOT_ANSWER_TAG

secure_random = random.SystemRandom()

class Command(BaseCommand):
    help = 'Restore VOTE question from file'

    def handle(self, *args, **options):

        for question in Question.objects.filter(tags__text=BOT_QUESTION_TAG):
            print(question.text)
            print(question.tags)

            right_answer = question.choice_set.filter(tags__text=BOT_ANSWER_TAG).first()
            second_answer = secure_random.choice(question.choice_set.all())

            question = do_question_save(
                text=question.text,
                tags=[{'id': 607}],
                answer_type=ANSWER_VOTE,
                choice_set=[
                    {'text': right_answer.text, 'tags': [{'id': 608}]},
                    {'text': second_answer.text, 'tags': []},
                ]
            )
            print(question.text)
            print(question.choice_set.all())

