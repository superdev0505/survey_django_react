from django.core.management.base import BaseCommand

from survey.submodels.article import Article


class Command(BaseCommand):
    help = 'Run integration test of creating survey and passing it with different conditions'

    def handle(self, *args, **options):
        for a in Article.objects.all():
            print(a.title)
            print(str.lower(a.title.replace(' ', '-')))
            a.url = str.lower(a.title.replace(' ', '-'))
            a.save()