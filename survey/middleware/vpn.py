import logging
import re
from datetime import timedelta

import requests
from django.http import HttpResponseRedirect
from django.utils import timezone

from django_server.utils import is_bot, get_client_ip
from survey.models import UserFlags
from survey.submodels.vpn import Vpn

logger = logging.getLogger(__name__)


ip_whitelist = [
    '127.0.0.1',
    '176.10.237.244',
    '79.195.103.53'
]

url_whitelist = [
    '/vpn',
    '/sw.js',
    '/favicon.ico',
    '/manifest.json',
    '/update_view/',
    '/error/vpn/',
    '/error/vpn',
    '/feedback/'
]

url_prefixes = [
    'article_images',
]

pattern = re.compile('^/' + '|'.join(url_prefixes) + '/.*')


class VPNMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if VPNMiddleware.is_vpn(request):
            return HttpResponseRedirect('/error/vpn')
        else:
            return self.get_response(request)

    @staticmethod
    def is_vpn(request):
        user = request.user
        ip = get_client_ip(request)

        if (request.path_info in url_whitelist) or (ip in ip_whitelist) or pattern.match(request.path_info):
            return False

        if user.is_anonymous:
            return False

        if is_bot(request):
            logger.info('[IS_VPN] Is Robot {0} - {1}'.format(ip, request.META.get('HTTP_USER_AGENT')))
            return False

        vpn = Vpn.get_by_ip(ip)
        # logger.info('[IS_VPN] check {}'.format(vpn))

        if vpn and (vpn.created > (timezone.now() - timedelta(weeks=2))):
            if vpn.is_vpn:
                logger.info('[IS_VPN] {0} - {1}'.format(ip, request.user))
                return True
        else:

            try:
                response = VPNMiddleware.check_iquality_info(ip, user)
                if response:
                    logger.info('[IS_VPN REQUEST] {0} - {1} - {2}'.format(ip, response, user))
                    UserFlags.objects.create(user=request.user, key=UserFlags.VPN)
                    return True
                else:
                    logger.info('[IS_VPN REQUEST] not vpn {0} - {1} - {2}'.format(ip, response, user))
            except Exception as e:
                logger.error('[IS_VPN] request timeout {0} - {1}'.format(ip, e))
        return False

    @staticmethod
    def check_iphub_info(ip, user):
        response = requests.get('http://v2.api.iphub.info/ip/{}'.format(ip), headers={
            'X-Key': 'NTMzMzpEVXdVaFdRdHdIR3UwT3VGV3hUdldYc0ZtVXVCYjV4cQ=='
        }, timeout=3).json()
        logger.info('[IS_VPN REQUEST] iphub {}'.format(response))

        vpn = Vpn.set_by_ip(ip, response.get('block') > 0)

        if vpn.is_vpn:
            return response

    @staticmethod
    def check_iquality_info(ip, user):
        response = requests.get('https://www.ipqualityscore.com/api/json/ip/VloVwex6edRJfsgR41xZO6vmsIrxbqqR/{}'.format(ip), timeout=3).json()

        if response.get('success'):
            logger.info('[IS_VPN REQUEST] {0} - {1} - {2}'.format(ip, response, user))
            is_vpn = response.get('vpn') or response.get('proxy') or response.get('tor')

            vpn = Vpn.set_by_ip(ip, is_vpn)

            if vpn.is_vpn:
                return response

