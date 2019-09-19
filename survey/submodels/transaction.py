import logging

import requests
from django.db.models import *
from django.utils import timezone

from django_server.db import DEFAULT_STRING_LENGTH, MEDIUM_STRING_LENGTH, NANO_STRING_LENGTH
from survey.models import SurveyUser
from survey.submodels.price import Price
from survey.submodels.provider import Provider, PAYOUT_USER_BITCOIN, PAYOUT_DEFAULT, PAYOUT_PROVIDER_BITCOIN
from survey.submodels.survey import Survey
from survey.subviews.payout import faucethub

logger = logging.getLogger(__name__)


TXN_NEW = 0
TXN_SUCCESS = 1
TXN_REJECTED = 2
TXN_STATUS = (
    (TXN_NEW, 'New'),
    (TXN_SUCCESS, 'Success'),
    (TXN_REJECTED, 'Rejected'),
)

USD_CURRENCY = 'USD'


class Transaction(Model):
    to_account = CharField(max_length=DEFAULT_STRING_LENGTH, default='')
    amount = DecimalField(default=0, max_digits=12, decimal_places=8)
    status = IntegerField(default=TXN_NEW, choices=TXN_STATUS)
    date_created = DateTimeField(default=timezone.now)
    date_sent = DateTimeField(default=None, null=True)
    survey = ForeignKey(Survey, on_delete=CASCADE, blank=True, null=True)

    # Fields in payment system
    payout_id = BigIntegerField(default=0)
    payout_status = IntegerField(default=0)
    payout_currency = CharField(max_length=NANO_STRING_LENGTH, default='')
    payout_user_hash = CharField(max_length=MEDIUM_STRING_LENGTH, default='')

    def __str__(self):
        return '{}  {}  {}  {}'.format(self.date_created, self.id, self.to_account, self.status)

    class Meta:
        abstract = True

    # Main Payout Strategy
    @classmethod
    def do_payout(cls, survey, is_mobile, user_ip, command=None):
        user = survey.user

        if cls.already_paid(survey):
            logger.error('[Payout] Transaction already paid {} - {}'.format(user, survey))
            return False

        if not hasattr(user, 'provider'):
            logger.info('[Payout] - Guest {} finished survey cycle'.format(user))
            return True

        provider = Provider.objects.filter(name=survey.user.provider).first()
        if not provider:
            logger.error('[Payout] problem sending payout {} - {}'.format(survey, provider))
            return False

        amount = Price.get_amount(user.country, provider, is_mobile)
        postback_url = provider.get_postback_url(is_mobile)

        data = survey.user.__dict__
        data['price'] = "%.5f" % amount
        data['ip'] = user_ip
        data['txn_id'] = survey.id

        logger.info('[Payout] user: {} from {}'.format(user.provider_user_id, 'MOBILE' if is_mobile else 'DESKTOP'))
        logger.info('[Payout] total price list amount: {}'.format(amount))
        logger.info('[Payout] provider: {}'.format(provider))
        logger.info('[Payout] provider payout method: {}'.format(provider.payout_method))

        # Payment to User and Provider with specified rate
        if provider.payout_method == PAYOUT_USER_BITCOIN:
            user_amount = amount * (provider.provider_payout_percent / 100)
            provider_amount = amount * ((100 - provider.provider_payout_percent) / 100)

            logger.info('[Payout] provider amount: {}'.format(provider_amount))
            logger.info('[Payout] user amount: {}'.format(user_amount))

            # Send User transaction
            user_transaction = UserTransaction.create(survey, user_amount)
            faucethub.send_money_request(user_transaction, user_ip)

            # Only save Provider transaction
            logger.info('[Payout] prepare to send - USR_BTC - {} -- {} -- {}'.format(provider, user.id, amount))
            ProviderTransaction.create(survey, provider_amount)
            logger.info('[Payout] sent {} {} - blank postback, did payout to Faucet for user = {} and later for provider = {}'.format(provider, user, user_amount, provider_amount))

        # Provider with BTC payment at the end of the day
        elif provider.payout_method == PAYOUT_PROVIDER_BITCOIN:
            ProviderTransaction.create(survey, amount)
            url = postback_url.format(**data)
            logger.info('[Payout] prepare to send - PRV_BTC - {} -- {} -- {} -- {}'.format(provider, url, user.id, amount))
            resp = requests.get(url, verify=False, timeout=7)
            logger.info('[Payout] sent {} {} - did postback, saving transaction to send later to provider, {}, {}'.format(provider, user, resp, resp.text))

        # Regular provider with simple postbacks
        elif provider.payout_method == PAYOUT_DEFAULT and postback_url:
            url = postback_url.format(**data)
            logger.info('[Payout] prepare to send - PRV_PBK - {} -- {} -- {} -- {}'.format(provider, url, user.id, amount))
            resp = requests.get(url, verify=False, timeout=7)
            logger.info('[Payout] sent {} {} {}'.format(provider, resp, resp.text))
            transaction = ProviderTransaction.create(survey,amount)
            transaction.to_account=survey.user.provider_user_id
            transaction.payout_status=resp.status_code
            transaction.payout_currency=USD_CURRENCY
            transaction.date_sent=timezone.now()
            transaction.status=TXN_SUCCESS
            transaction.save()

        else:
            logger.error('[Payout] - {} - postback url is empty or payout method unknown'.format(provider))
            if command:
                command.stdout.write('[Payout] - {} - postback url is empty or payout method unknown'.format(provider))

        return True

    @classmethod
    def already_paid(cls, survey):
        return survey.providertransaction_set.count() > 0 or survey.usertransaction_set.count() > 0


class ProviderTransaction(Transaction):
    provider = ForeignKey(Provider, on_delete=CASCADE)

    class Meta:
        ordering = ['-date_created']
        verbose_name = 'Transaction - Provider'
        indexes = [
            Index(fields=['provider']),
        ]

    @staticmethod
    def create(survey, amount):
        return ProviderTransaction.objects.create(
            survey=survey,
            amount=amount,
            provider=survey.user.provider,
            to_account=survey.user.provider.bitcoin_address
        )


class UserTransaction(Transaction):
    user = ForeignKey(SurveyUser, on_delete=CASCADE)

    class Meta:
        ordering = ['-date_created']
        verbose_name = 'Transaction - User'
        indexes = [
            Index(fields=['user']),
        ]

    @staticmethod
    def create(survey, amount):
        return UserTransaction.objects.create(
            survey=survey,
            amount=amount,
            user=survey.user,
            to_account=survey.user.bitcoin_address
        )