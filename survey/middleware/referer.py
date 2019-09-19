import logging
import re
from django import urls
from django.shortcuts import redirect

from django_server.settings import ALLOWED_HOSTS

logger = logging.getLogger(__name__)


WHITELIST_URLS = [
    '/error/',
    '/static/',
    '/offerwall/',
    '/referer/'
]
WHITELIST_URL_RE = re.compile('^({}).*'.format(str.join('|', WHITELIST_URLS)))

ALLOWED_REFERRERS = [
    'localhost',
    'moretvtime',
    'junglesurvey',
    'google',
    'yahoo',
    'bing',
    'yandex',
    'facebook',
    'linkedin',
    'vk',
    'ok',
    'vkontakte',
    'twitter',
    'twitch',
    'discord',
]


# Precompiled regular expression for allowed hosts
ALLOWED_REFERRERS_RE = re.compile('^http(?:s)?://(?:[\w-]+\.)*({}).*'.format(str.join('|', ALLOWED_REFERRERS)))

ALLOWED_HOSTS_RE = re.compile('^http(?:s)?://(?:[\w-]+\.)*({})'.format(str.join('|', ALLOWED_HOSTS)))


class RefererMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if WHITELIST_URL_RE.search(request.path):
            return self.get_response(request)

        ref = request.META.get('HTTP_REFERER', '')
        if ref and not ALLOWED_HOSTS_RE.search(ref):

            if ALLOWED_REFERRERS_RE.search(ref):
                # if request.user.is_anonymous or not request.user.social_auth.count():
                return self.get_response(request)
                # elif request.user.survey_set.count() > 1:  # If user ever answered survey, offer him to change refId
                #     return redirect('/referer')
                # else:
                #     return self.get_response(request)

            logger.info('[WRONG REFERER] {}'.format(ref))
            return redirect(urls.reverse('survey:error_referer'))

        return self.get_response(request)
