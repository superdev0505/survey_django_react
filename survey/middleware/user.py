import logging
import re

from django.shortcuts import redirect

from django_server.utils import get_client_country, get_client_ip
from survey.models import IPHistory, UserBanHistory

logger = logging.getLogger(__name__)

url_whitelist = [
    '/',
    '/ban',
    '/sw.js',
    '/favicon.ico',
    '/manifest.json',
    '/update_view/',
    '/error/ban/',
    '/error/ban',
    '/error/suspend/',
    '/error/suspend',
    '/feedback/',
    '/admin/',
]

user_agent_white_list = [
    "Mediapartners-Google"
]


class UserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        user = request.user

        if user and not user.is_anonymous and not user.country:
            country = get_client_country(request)
            if country:
                user.country = country
                user.save()

        is_google = request.META.get('HTTP_USER_AGENT') in user_agent_white_list

        # Ban section
        user_ip = get_client_ip(request)
        if not is_google and user and hasattr(user, 'provider') and (not user.is_anonymous) and (request.path_info not in url_whitelist) and not str.startswith(request.path_info, '/offerwall'):
            if not user.is_active:
                return redirect('/error/ban')
            # if user_ip in IPHistory.get_blacklist():
            #     return redirect('/error/ban')
            # if user.is_suspended:
            #     logger.info('[SUSPENDED] user {}'.format(user))
            #     success_unblock = UserBanHistory.unblock_user(user)
            #     if not success_unblock:
            #         return redirect('/error/suspend')

        return self.get_response(request)
