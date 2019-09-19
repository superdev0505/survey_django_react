import logging
import re
import uuid
import qrcode
import qrcode.image.svg

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view, permission_classes

from django_server import utils
from django_server.utils import get_client_ip, get_client_country, is_mobile
from survey.models import RefIdHistory
from survey.submodels.price import Price
from survey.submodels.provider import Provider, PAYOUT_USER_BITCOIN, PROVIDER_SWAGBUCKS_ID
from survey.subviews.payout import faucethub

logger = logging.getLogger(__name__)


def offerwall_help(request):
    template = 'survey/offerwall/help.html'
    return render(request, template, {})


def offerwall_qr(request):
    ref_id = request.GET.get('ref_id')
    if re.search('^[A-Za-z0-9]{8}$', ref_id):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=5, border=0)
        qr.add_data('https://moretvtime.com/survey/?ref_id={}'.format(ref_id))
        qr.make(fit=True)
        qr = qr.make_image()
        response = HttpResponse(content_type="image/png")
        qr.save(response, "PNG")
        return response
    else:
        return HttpResponse(status_code=403)


def offerwall_provider(request, provider):
    return offerwall_user


def offerwall_user(request, provider, sub_id=None):
    template = 'survey/offerwall/index.html'

    if not provider:
        logger.error('[Offerwall] Provider is empty'.format(provider, sub_id))
        return render(request, template, {'error': 'Please, provide company name and user_id to continue'})

    provider_object = Provider.objects.filter(id=provider).first()
    if not provider_object:
        logger.error('[Offerwall] Company {} is not registered'.format(provider))
        return render(request, template, {'error': 'Company {} is not registered'.format(provider)})

    if not sub_id or sub_id == 'USER-ID-HERE':
        if provider_object.payout_method == PAYOUT_USER_BITCOIN or provider_object.name == 'swagbucks':
            sub_id = str(uuid.uuid4())
        else:
            logger.error('[Offerwall] UserId is empty'.format(provider))
            return render(request, template, {'error': 'Please, provide user_id to continue'.format(provider)})

    provider = provider_object
    reference = RefIdHistory.get_or_create_reference(provider, sub_id)
    country = get_client_country(request)

    # Swagbucks has own conditions of autoredirect
    if provider.id == PROVIDER_SWAGBUCKS_ID:
        return redirect('https://moretvtime.com?ref_id=' + reference.id)

    amount_mobile = Price.get_amount(country, provider, True)
    amount_mobile = amount_mobile * (provider.provider_payout_percent / 100)

    amount_desktop = Price.get_amount(country, provider, False)
    amount_desktop = amount_desktop * (provider.provider_payout_percent / 100)

    response = render(request, template, {
        'sub_id': sub_id,
        'provider': provider,
        'reference': reference,
        'amount_desktop': str(amount_desktop)[:6],
        'amount_mobile': str(amount_mobile)[:6],
        'bitcoin': provider.is_user_accepting_bitcoin,
        'bitcoin_masked': utils.mask_btc_address(reference.bitcoin_address)
    })

    http_referer = request.META.get('HTTP_REFERER')
    if http_referer:
        response['X-Frame-Options'] = 'allow-from ' + http_referer

    return response


@api_view(['POST'])
@permission_classes([])
def profile(request):
    data = request.data
    ip = get_client_ip(request)

    if not len(data):
        return JsonResponse({'success': False, 'error': 'No data'}, status=400)

    provider = Provider.objects.filter(name=data.get('provider')).first()
    reference = RefIdHistory.objects.filter(provider=provider, provider_user_id=data.get('sub_id')).first()
    if not reference:
        return JsonResponse({'success': True})

    if reference.bitcoin_address:
        return JsonResponse({'success': False, 'error': 'Bitcoin address already associated with current user'}, status=403)

    try:
        bitcoin_address = data.get('address')
        logger.info('[Offerwall] - profile - {} - {} - {}'.format(ip, reference, bitcoin_address))

        # TODO
        # if RefIdHistory.objects.filter(bitcoin_address=bitcoin_address).count() > 0:
        #     return JsonResponse({'success': False, 'error': 'Bitcoin address already in use'}, status=403)

        faucethub.check_address(bitcoin_address)
        reference.bitcoin_address = bitcoin_address
        reference.save()
    except Exception as e:
        logger.error('[Offerwall] - profile - {} - {}'.format(ip, e))
        return JsonResponse({'success': False, 'error': str(e)}, status=403)

    return JsonResponse({'success': True})
