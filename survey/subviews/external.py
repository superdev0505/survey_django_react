import logging

from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes

from django_server.utils import get_client_ip
from survey.models import SurveyUser
from survey.submodels.transaction import ProviderTransaction

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([])
def external_postback(request):
    ref_id = request.GET.get('ref_id')
    sign = request.GET.get('sign')

    client_ip = get_client_ip(request)
    if sign not in ['m0lu9mackkn6lsc4gqaq3wiejtxagiye', 'ffoedqu5k39sjyu3zuqa5le3o9obq8o7']:
        logger.error('[EXTERNAL] postback - wrong signature - {} - {} - {}'.format(client_ip, sign, ref_id))
        return JsonResponse({'error': 'wrong signature'}, status=403)

    user = SurveyUser.objects.filter(ref_id=ref_id).first()
    if not user:
        logger.error('[EXTERNAL] postback - wrong user id - {} - {} - {}'.format(client_ip, sign, ref_id))
        return JsonResponse({'error': 'wrong ref_id'}, status=403)

    logger.error('[EXTERNAL] postback - PAYOUT - {} - {} - {}'.format(client_ip, sign, ref_id))
    return JsonResponse({'status': 'ok'}, status=200)

