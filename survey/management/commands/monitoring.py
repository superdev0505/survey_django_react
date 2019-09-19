import logging
import random
from datetime import timedelta
from time import sleep

from django.core.management.base import BaseCommand
from django.utils import timezone

from survey.models import SurveyUser
from survey.serializers import MetricSerializer
from survey.submodels.metrics import Metric
from survey.submodels.survey import Survey, QuestionAnswer, SURVEY_STATUS_BOT, SURVEY_STATUS_NEW, SURVEY_STATUS_SUCCESS
from survey.submodels.transaction import ProviderTransaction, UserTransaction

logger = logging.getLogger(__name__)

secure_random = random.SystemRandom()


class Command(BaseCommand):
    help = 'Cron job for monitoring transactions'

    def handle(self, *args, **options):

        delta = timezone.now() - timedelta(minutes=5)

        metric = Metric.objects.create(
            survey=Survey.objects.filter(created__gte=delta).count(),
            questions=QuestionAnswer.objects.filter(created__gte=delta).count(),
            survey_success=Survey.objects.filter(created__gte=delta, status=SURVEY_STATUS_SUCCESS).count(),
            survey_unsuccess=Survey.objects.filter(created__gte=delta).exclude(status__in=(SURVEY_STATUS_NEW, SURVEY_STATUS_SUCCESS)).count(),
            transaction=ProviderTransaction.objects.filter(date_sent__gte=delta).count() + UserTransaction.objects.filter(date_sent__gte=delta).count(),
            users_registered=SurveyUser.objects.filter(date_joined__gte=delta).count(),
        )

        logger.info('[METRIC] {}'.format(MetricSerializer(metric).data))

