import logging

import requests
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.decorators import api_view

from django_server.settings import FAUCETHUB_API_KEY
from survey.submodels.price import BTCPrice

logger = logging.getLogger(__name__)


FAUCETHUB_URL = 'https://faucethub.io/api/v1/'
FAUCETHUB_CURRENCY = 'BTC'


@api_view(['POST'])
def FaucethubCheckBalance(request):
    url = FAUCETHUB_URL + 'balance'
    data = {'api_key': FAUCETHUB_API_KEY, 'currency': FAUCETHUB_CURRENCY}
    r = requests.post(url, data=data)
    return HttpResponse(r)


def check_address(address):
    url = FAUCETHUB_URL + 'checkaddress'
    data = {'api_key': FAUCETHUB_API_KEY, 'address': address, 'currency': FAUCETHUB_CURRENCY}
    response = requests.post(url, data=data).json()
    status = response.get('status')
    if status == 412:
        raise Exception('Wrong address provided', status)
    if response.get('status') != 200:
        raise Exception(response.get('message'), status)


##
# Method to send Faucethub wallet transaction for specific company user and wallet
#
def send_money_request(transaction, ip):
    from survey.submodels.transaction import TXN_NEW

    if transaction.status != TXN_NEW:
        logger.error('[FaucetHub] - transaction has already been sent: {}'.format(transaction))
        return

    response = do_send_money(transaction.amount, transaction.to_account, ip)

    if response.get('status') == 200:
        transaction.payout_id = response.get('payout_id')
        transaction.payout_status = response.get('status')
        transaction.payout_currency = FAUCETHUB_CURRENCY
        transaction.payout_user_hash = response.get('payout_user_hash')
        transaction.date_sent = timezone.now()
        transaction.status = 1
        transaction.save()
        logger.info('[FaucetHub] - sent')
    else:
        logger.error('[FaucetHub] - Problem when saving santoshi - response {}'.format(response))


def do_send_money(amount, to_account, ip=None):
    price = BTCPrice.get_today_amount()

    logger.info('[FaucetHub] - today price of Satoshi: {}'.format(price))
    logger.info('[FaucetHub] - transaction.amount: {}'.format(amount))

    amount = amount / price

    logger.info('[FaucetHub] - formula: {{transaction.amount / Satoshiprice}} -- {}'.format(amount))

    if amount <= 0.0:
        return

    logger.info('[FaucetHub] - send to user wallet, ip:{} - amount:{} - account:{} '.format(ip, amount, to_account))

    url = FAUCETHUB_URL + 'send'
    data = {'api_key': FAUCETHUB_API_KEY,
            'to': to_account,
            'amount': int(amount),
            'currency': FAUCETHUB_CURRENCY,
            'ip_address': ip}

    logger.info('[FaucetHub] - send_money_request - prepare: ' + str(data))
    response = requests.post(url, data=data).json()
    logger.info('[FaucetHub] - send_money_request - sent ' + str(response))
    return response
