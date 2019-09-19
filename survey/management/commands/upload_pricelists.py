import csv
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from survey.countries import COUNTRIES
from survey.models import SurveyUser
from survey.submodels.price import Price
from survey.submodels.provider import Provider


class Command(BaseCommand):
    help = 'Upload new pricelists'

    def handle(self, *args, **options):

        with open('survey/management/commands/pricelist.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            Price.objects.all().delete()

            for row in reader:
                price = Price(
                    country=row.get('country'), #COUNTRIES.get(row.get('country')),
                    provider=Provider.objects.filter(name=row.get('provider')).first(),
                    mobile=row.get('mobile'),
                    desktop=row.get('desktop'))

                if not price.provider and not price.country:
                    print('[ATTENTION] - can not recognize country or provider: {}'.format(row))
                    continue

                price.save()
                print(price)