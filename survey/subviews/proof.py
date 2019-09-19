import hashlib
import logging
from django.core.cache import cache

from django_server.utils import is_mobile, get_client_ip
from survey.models import UserFlags

logger = logging.getLogger(__name__)


MINUTE = 60
HOURS_24 = 24 * 60 * 60
PROOF_KEY = 'PROOF_KEY_{}'
PROOF_KEY_PREV = 'PROOF_KEY_PREV_{}'
PROOF_SECRET = '91hsda09uo123hkagsdf7123jghhsba09'


# Creating sign to send with question response
def try_set_proof(user, survey):

    new_sign = hashlib.sha256(str(
        '{}-{}'.format(survey.id, user.id, PROOF_SECRET)
    ).encode('utf-8')).hexdigest()

    cache.set(PROOF_KEY.format(user.id), new_sign, timeout=MINUTE)

    return new_sign


def check_proof(request):
    user = request.user

    if request.user.is_authenticated and (request.method != 'POST' or not user.is_registered):
        return

    ip = get_client_ip(request)
    sign = request.data.get('s')
    movements = request.data.get('m')
    mouse_clicks = request.data.get('mc')
    keyboard_clicks = request.data.get('kd')
    fingerprint = request.data.get('fingerprint')
    cached_sign = cache.get(PROOF_KEY.format(user.id))

    # TODO temporarry pass if fingerpring appeared in request
    if fingerprint:
        return

    if mouse_clicks or keyboard_clicks:
        click_key = 'PROOF_CLICK_{}'.format(user.id)
        previous_click = cache.get(click_key)
        if previous_click == str(mouse_clicks):
            logger.info('[PROOF] clicks SUSPICIOUS: {} - {} - {} - {} - {}'.format(ip, user, request.user_agent, mouse_clicks, keyboard_clicks))
        cache.set(click_key, str(mouse_clicks))

        logger.info('[PROOF] clicks: {} - {} - {} - {} - {}'.format(ip, user, request.user_agent, mouse_clicks, keyboard_clicks))
        return

    # if not cached_sign:
    #     logger.info('[PROOF] suspicious - no sign for a long time {} - {}'.format(ip, user))

    if sign != cached_sign:
        logger.info('[PROOF] suspicious - sign not equals cached: {} - {} - {} - {}'.format(ip, user, sign, cached_sign))

    if not movements or not len(movements):
        if is_mobile(request):
            pass
        else:
            logger.info('[PROOF] suspicious - No movements on Desktop: {} - {} - {} - {} - {} - {}'.format(ip, user, sign, cached_sign, movements, request.user_agent))
            UserFlags.objects.create(user=user, key=UserFlags.NO_MOUSE)
    else:
        if is_mobile and len(movements) > 1:
            logger.info('[PROOF] suspicious - Mouse on mobile 0_o : {} - {} - {} - {} - {} - {}'.format(ip, user, sign, cached_sign, movements, request.user_agent))
            UserFlags.objects.create(user=user, key=UserFlags.MOUSE_PH)

    cache.set(PROOF_KEY_PREV.format(user.id), sign, timeout=HOURS_24)