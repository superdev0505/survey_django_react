import logging
import random
import traceback

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Sum
from django.utils import timezone

from survey.submodels.provider import Provider, PAYOUT_USER_BITCOIN, PAYOUT_PROVIDER_BITCOIN
from survey.submodels.transaction import Transaction, ProviderTransaction, TXN_NEW, TXN_SUCCESS
from survey.subviews.payout import faucethub
from survey.subviews.payout.faucethub import FAUCETHUB_CURRENCY

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run daily Faucethub payouts to providers'

    def handle(self, *args, **options):

        for transaction in ProviderTransaction.objects \
                .filter(status=TXN_NEW, provider__payout_method__in=[PAYOUT_PROVIDER_BITCOIN, PAYOUT_USER_BITCOIN]) \
                .values('provider__id') \
                .annotate(amount=Sum('amount')) \
                .order_by('provider_id'):

            try:
                provider = Provider.objects.filter(id=transaction.get('provider__id')).first()
                amount = transaction.get('amount')
                to_account = provider.bitcoin_address

                logger.info( '[Payout] - send to provider wallet provider:{} - amount:{} - account:{} '.format(provider, amount, to_account))

                response = faucethub.do_send_money(amount, to_account)

                if response.get('status') == 200:
                    txns = ProviderTransaction.objects.filter(status=TXN_NEW, provider=provider).count()
                    logger.info('[Payout] count of transactions to update: {}'.format(txns))
                    ProviderTransaction.objects.filter(status=TXN_NEW, provider=provider).update(
                        payout_id=response.get('payout_id'),
                        payout_status=response.get('status'),
                        payout_currency=FAUCETHUB_CURRENCY,
                        payout_user_hash=response.get('payout_user_hash'),
                        date_sent=timezone.now(),
                        status=TXN_SUCCESS
                    )
                    logger.info('[Payout] - sent')
                else:
                    logger.error('[Payout] - Problem when saving transactions - response {}'.format(response))

            except  Exception as e:
                logger.error('[Payout] {}'.format(e))
                traceback.print_exc()

        logging.info('[Payout] Finished payment')
