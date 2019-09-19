from django.contrib.postgres.fields import ArrayField
from django.db.models import *
from django_countries.fields import CountryField

from django_server.db import NANO_STRING_LENGTH, LONG_STRING_LENGTH, SHORT_STRING_LENGTH

PAYOUT_DEFAULT = 'default'
PAYOUT_USER_BITCOIN = 'user_bitcoin'
PAYOUT_PROVIDER_BITCOIN = 'provider_bitcoin'
PAYOUT_METHODS = (
    (PAYOUT_DEFAULT, 'Default - manual end of month'), # we pay at the end of the month paypal
    (PAYOUT_USER_BITCOIN, 'User - FH provider + FH user'), # we pay user after complete and provider get paid at the end of the day
    (PAYOUT_PROVIDER_BITCOIN, 'Provider - FH postback') # once user finish the survey we send postback and we pay only to the provider at the end of the day
)

DEFAULT_QUESTION_COUNT = 10

PROVIDER_SWAGBUCKS_ID = 121


class Provider(Model):
    name = TextField('name', default='', blank=False, null=False)
    postback_url = TextField('postback url', default='', blank=True, null=True, help_text='Possible variables: {provider_user_id} {country} {price} {ip} {bitcoin_address} {txn_id}')
    currency = CharField(max_length=SHORT_STRING_LENGTH, default='cents')
    question_count = IntegerField('Count of questions per survey', default=DEFAULT_QUESTION_COUNT)

    payout_method = CharField(max_length=SHORT_STRING_LENGTH, choices=PAYOUT_METHODS, default=PAYOUT_DEFAULT)
    bitcoin_address = CharField(max_length=LONG_STRING_LENGTH, default='', blank=True)
    provider_payout_percent = DecimalField('provider payout percent to user', decimal_places=2, default=0, max_digits=4)
    payout_hide = BooleanField('Hide user payout', default=False)

    is_static_postback = BooleanField(default=False)
    static_postback_mobile = TextField('static postback mobile', default='', blank=True, null=True, help_text='Possible variables: {provider_user_id} {country} {price} {ip} {bitcoin_address} {txn_id}')
    static_postback_desktop = TextField('static postback desktop', default='', blank=True, null=True, help_text='Possible variables: {provider_user_id} {country} {price} {ip} {bitcoin_address} {txn_id}')
    static_postback_countries = ArrayField(CountryField(blank=True, null=True), default=list, blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def is_accepting_bitcoin(self):
        return self.payout_method == PAYOUT_PROVIDER_BITCOIN or self.payout_method == PAYOUT_USER_BITCOIN

    @property
    def is_user_accepting_bitcoin(self):
        return self.payout_method == PAYOUT_USER_BITCOIN

    def get_postback_url(self, is_mobile):
        return (self.static_postback_mobile if is_mobile else self.static_postback_desktop) if self.is_static_postback else self.postback_url