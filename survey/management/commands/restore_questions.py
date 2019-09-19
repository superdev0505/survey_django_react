import csv

from django.core.management.base import BaseCommand

from survey.admin_views import do_question_save
from survey.submodels.survey import ANSWER_VOTE


class Command(BaseCommand):
    help = 'Restore VOTE question from file'

    def handle(self, *args, **options):

        with open('survey/management/commands/vote_questions.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                question = do_question_save(text=row['question'], answer_type=ANSWER_VOTE, choice_set=[
                    {'text': row['answer1']},
                    {'text': row['answer2']},
                ])
                print(question)