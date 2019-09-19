import hashlib
import logging
import re
import traceback
from subprocess import Popen, PIPE, STDOUT

import requests

from django.contrib.gis.geoip2 import GeoIP2
from django.utils import timezone
from geoip2.errors import AddressNotFoundError

logger = logging.getLogger(__name__)

RE_MOBILE_UA = '"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw-(n|u)|c55/|capi|ccwa|cdm-|cell|chtm|cldc|cmd-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc-s|devi|dica|dmob|do(c|p)o|ds(12|-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(-|_)|g1 u|g560|gene|gf-5|g-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd-(m|p|t)|hei-|hi(pt|ta)|hp( i|ip)|hs-c|ht(c(-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i-(20|go|ma)|i230|iac( |-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|-[a-w])|libw|lynx|m1-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|-([1-8]|c))|phil|pire|pl(ay|uc)|pn-2|po(ck|rt|se)|prox|psio|pt-g|qa-a|qc(07|12|21|32|60|-[2-7]|i-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h-|oo|p-)|sdk\/|se(c(-|0|1)|47|mc|nd|ri)|sgh-|shar|sie(-|m)|sk-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h-|v-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl-|tdg-|tel(i|m)|tim-|t-mo|to(pl)|ts(70|m-|m3|m5)|tx-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas-|your|zeto|zte-"'
RE_ROBOT_UA = 'bot|crawl|slurp|spider|google|mediapartners|facebookexternalhit|yandex'


def is_mobile(request):
    try:
        return request.user_agent.is_mobile or request.user_agent.is_tablet
    except Exception as e:
        try:
            return re.search(RE_MOBILE_UA, request.META.get('HTTP_USER_AGENT'), re.IGNORECASE)
        except Exception as e:
            traceback.print_exc()
            logger.error('[UTILS] Wrong User agent {}'.format(e))
            return False


def is_bot(request):
    try:
        return request.user_agent.is_bot
    except Exception as e:
        return re.search(RE_ROBOT_UA, request.META.get('HTTP_USER_AGENT'), re.IGNORECASE)


def get_user_agent(request):
    return request.META.get('HTTP_USER_AGENT')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_client_country(request):
    country = ''
    try:
        ip = get_client_ip(request)
        country = GeoIP2().country_code(ip)
    except AddressNotFoundError as e:
        logger.error('[get_client_country] ' + str(e))
        pass

    return country


def get_client_city(request):
    city = ''
    try:
        ip_address = get_client_ip(request)
        city = GeoIP2().city(ip_address)
    except Exception as e:
        logger.error('[get_client_country] ' + str(e))

    return city


def generate_user_id(request):
    return hashlib.sha256(str(
        get_client_ip(request) +
        get_user_agent(request) +
        str(timezone.now())
    ).encode('utf-8')).hexdigest()


def mask_btc_address(btc):
    ln = 4 # count of symbols to show at start and end
    if not btc or len(btc) < ln * 2:
        return btc
    return ('{}{:*>'+str(len(btc) - (ln * 2))+'}').format(btc[:ln], btc[-ln:])


def cmd_execute(command, line_callback=None):
    process = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)

    # Poll process for new output until finished
    output = ''
    while True:
        nextline = str(process.stdout.readline(), encoding='utf-8')
        output = output + nextline
        if nextline == '' and process.poll() is not None:
            break
        if line_callback:
            line_callback(nextline)

    process.communicate()

    return str(output)