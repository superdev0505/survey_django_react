import random
import re

from django_server import settings
from django_server.utils import is_mobile
from survey.submodels.banner import Banner
from survey.submodels.provider import PROVIDER_SWAGBUCKS_ID

BANNERS = []

# Counter to rotate bidding company
bidding_counter = 0
bidding_mobile = [
    'https://adxbid.me/hbgsript_mobile_41.js',
    'https://adxbid.me/hbgsript_datawrkz_mobile_41.js',
    'https://adxbid.me/hbgsript_velis_mobile_41.js'
]
bidding_desktop = [
    "https://adxbid.me/hbgsript_desktop_41.js",
    "https://adxbid.me/hbgsript_datawrkz_desktop_41.js",
    "https://adxbid.me/hbgsript_velis_desktop_41.js"
]

def context(request):
    context = {}
    user = request.user

    is_mobile_device = is_mobile(request)
    if is_mobile_device:
        context['is_mobile'] = True

    context['recaptcha_key'] = settings.RECAPTCHA_V2_SITE_KEY

    if request.META['HTTP_HOST'] in ['moretvtime.com', 'moretvtime.com:8000', 'localhost:8000', 'dev.moretvtime.com']:

        # Show Banners only on specific domains
        banners = Banner.get_banner_set(is_mobile_device)
        context['banners'] = banners
        for banner in banners:
            context[banner.get('selector')] = banner

        # Show Blog and articles only on specific domains
        context['show_articles'] = True

        # Context of user
        if user and hasattr(user, 'provider') and (not user.is_anonymous):# and user.social_auth.count():
            context['user_authorized'] = True
            context['provider_id'] = user.provider.id
            # For provider swagbucks should have special flag
            context['is_swagbucks'] = user.provider.id == PROVIDER_SWAGBUCKS_ID

    # Test user cookie flag
    if request.COOKIES.get('is_test_user'):
        context['is_test_user'] = True

    # Including fingerprint check
    if random.random() > 0.8:
        context['fingerprint'] = True

    # All about bidding
    # global bidding_counter
    # bidding_urls = bidding_mobile if is_mobile_device else bidding_desktop
    # bidding_counter = bidding_counter + 1
    # if bidding_counter >= len(bidding_urls):
    #     bidding_counter = 0
    #
    # context['bidding_url'] = bidding_urls[bidding_counter]
    context['bidding_url'] = 'https://adxbid.me/hbgsript_velis_mobile_41.js' if is_mobile_device else "https://adxbid.me/hbgsript_velis_desktop_41.js"

    return context