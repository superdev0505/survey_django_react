import logging

from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from social_django.models import UserSocialAuth

from django_server.utils import generate_user_id
from survey.models import SurveyUser, USER_CAN_CHANGE_PROFILE_IN_DAY, RefIdHistory
from survey.submodels.provider import PAYOUT_USER_BITCOIN, PAYOUT_PROVIDER_BITCOIN

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([])
def signup_view(request):
    ref_id = request.data.get('ref_id')

    user = request.user
    if user.is_anonymous:
        try:
            user = get_user(request, ref_id)
            do_login(request, user)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=403)
    else:
        try:
            user.set_ref_id(ref_id)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=403)


@api_view(['POST'])
@permission_classes([])
def logout_view(request):
    request.session.flush()
    return HttpResponseRedirect('/')


def get_user(request, ref_id=None):
    ref = get_ref(ref_id) if ref_id else None

    if ref:
        if ref.user and ref.user.provider:
            return ref.user

        user = SurveyUser(username='{}:{}'.format(ref.provider, ref.provider_user_id),
                          ref_id=ref.id,
                          provider=ref.provider,
                          provider_user_id=ref.provider_user_id,
                          bitcoin_address=ref.bitcoin_address)
        user.save()
        ref.user = user
        ref.save()
        return user
    else:
        provider_user_id = request.session.session_key or generate_user_id(request)
        user = SurveyUser(username=provider_user_id, provider=None, provider_user_id=provider_user_id)
        user.save()
        return user


def get_ref(ref_id):
    ref = RefIdHistory.objects.filter(id=ref_id).first()
    if not ref:
        raise Exception('This is not a recognized Referral ID')
    if not ref.bitcoin_address and ref.provider.payout_method in [PAYOUT_USER_BITCOIN]:
        raise Exception('This is not a recognized Referral ID')
    # if ref.user and UserSocialAuth.objects.filter(user_id=ref.user.id).first():
    #     raise Exception('This Referral ID is already in use, login using associated social network')
    return ref


def do_login(request, user, **credentials):
    request.session.flush()
    authenticate(request)
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return request.user

