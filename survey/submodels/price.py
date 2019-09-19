import decimal
import logging

import requests

from django.db.models import *
from import_export import fields, resources
from django.utils import timezone
from django_countries.fields import CountryField
from import_export.resources import ModelResource
from import_export.widgets import ForeignKeyWidget

logger = logging.getLogger(__name__)

BTC_PRICE_URL = 'http://codacoin.com/api/public.php?request=convert&type=btctofiat&input=1&symbol=enabled&decimal=8&exchange=average&currency=USD&denom=satoshi'


MINIMAL_PRICE = 0.0002250

PRICE_TYPE_MOBILE = 'mobile'
PRICE_TYPE_DESKTOP = 'desktop'
PRICE_TYPE = (
    (PRICE_TYPE_DESKTOP, PRICE_TYPE_DESKTOP),
    (PRICE_TYPE_MOBILE, PRICE_TYPE_MOBILE)
)


class Price(Model):
    country = CountryField(default='', blank=True, null=True)
    mobile = DecimalField(default=MINIMAL_PRICE, max_digits=12, decimal_places=8)
    desktop = DecimalField(default=MINIMAL_PRICE, max_digits=12, decimal_places=8)
    provider = ForeignKey('Provider', null=True, blank=True, default=None, on_delete=CASCADE)

    class Meta:
        ordering = ['country']
        verbose_name = 'Price - USD'
        unique_together = [['country', 'provider']]

    def __str__(self):
        return '{} - {} - {} - {}'.format(self.country, self.provider, self.mobile, self.desktop)

    @classmethod
    def get_amount(cls, country, provider, is_mobile):
        price = Price.objects.filter(country=country, provider=provider).first()

        if not price:
            price = Price.objects.filter(country='', provider=provider).first()

        if not price:
            price = Price.objects.filter(country=country, provider=None).first()

        if not price:
            price = Price.objects.filter(country='', provider=None).first()

        if price:
            amount = getattr(price, PRICE_TYPE_MOBILE if is_mobile else PRICE_TYPE_DESKTOP)
            logger.info('[Price] selected - {}'.format(price))
        else:
            amount = decimal.Decimal(MINIMAL_PRICE)

        return amount * provider.question_count


class PriceResource(ModelResource):
    provider = fields.Field(
        column_name='provider',
        attribute='provider',
        widget=ForeignKeyWidget('Provider', 'name'))

    class Meta:
        model = Price
        import_id_fields = ['country', 'provider']
        fields = ['country', 'provider', 'mobile', 'desktop']


class BTCPrice(Model):
    date = DateField(auto_now_add=True)
    amount = DecimalField(default=0, max_digits=12, decimal_places=8)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Price - BTC'

    def __str__(self):
        return '{} - {}'.format(self.date, self.amount)

    @classmethod
    def get_today_amount(cls):
        price = BTCPrice.objects.filter(date=timezone.now()).first()
        if not price:
            price = requests.get(BTC_PRICE_URL).text.split('$')[1]
            price = BTCPrice.objects.create(amount=decimal.Decimal(price))
        return price.amount
