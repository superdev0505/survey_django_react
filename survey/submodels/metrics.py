import decimal

import requests

from django.db.models import *
from django.utils import timezone


class Metric(Model):
    date = DateTimeField(default=timezone.now)
    survey = IntegerField(default=0)
    questions = IntegerField(default=0)
    survey_success = IntegerField(default=0)
    survey_unsuccess = IntegerField(default=0)
    transaction = IntegerField(default=0)
    users_registered = IntegerField(default=0)

    def __str__(self):
        return self.date

    class Meta:
        indexes = [
            Index(fields=['date']),
        ]
