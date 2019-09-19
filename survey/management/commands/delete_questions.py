import csv

from django.core.management.base import BaseCommand

from survey.admin_views import do_question_save
from survey.submodels.survey import ANSWER_VOTE, Question


class Command(BaseCommand):
    help = 'Restore VOTE question from file'

    def handle(self, *args, **options):
        counter = 0
        not_found_counter = 0

        with open('survey/management/commands/delete_questions.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                question = Question.objects.filter(text=row['question'], choice__text=row['answer1']).first()
                if not question:
                    question = Question.objects.filter(text=row['question'], choice__text=row['answer2']).first()

                if not question:
                    question = Question.objects.filter(choice__text=row['answer1']).filter(choice__text=row['answer2']).first()
                    if question:
                        print('[STRANGE]')
                        print('[STRANGE] csv - {}'.format(row))
                        print('[STRANGE] d b - {} , {}'.format(question, list(question.choice_set.all())))
                        print('[STRANGE]')

                if not question:
                    question = Question.objects.filter(choice__text=row['answer1']).first()
                    if question:
                        print('[STRANGE]')
                        print('[STRANGE] csv - {}'.format(row))
                        print('[STRANGE] d b - {} , {}'.format(question, list(question.choice_set.all())))
                        print('[STRANGE]')

                if not question:
                    question = Question.objects.filter(choice__text=row['answer2']).first()
                    if question:
                        print('[STRANGE]')
                        print('[STRANGE] csv - {}'.format(row))
                        print('[STRANGE] d b - {} , {}'.format(question, list(question.choice_set.all())))
                        print('[STRANGE]')

                try:
                    if question:
                        print('[DELETE]' + str(question))
                        question.enabled = False
                        question.save()
                        counter = counter + 1
                    else:
                        print('[NOT FOUND] {}'.format(row))
                        not_found_counter = not_found_counter + 1
                except Exception as e:
                    print('[NO QUESTON] {}'.format(row['question']))

        print('[TOTAL DELTED] ' + str(counter))
        print('[TOTAL NOT DELTED] ' + str(not_found_counter))