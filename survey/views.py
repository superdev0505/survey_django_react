import logging
from datetime import timedelta

from django.conf.global_settings import CSRF_COOKIE_NAME
from django.db.models import Count, Q, Max
from django.db.models.expressions import RawSQL
from django.http import JsonResponse
from django.middleware import csrf
from django.shortcuts import render, redirect
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAdminUser
from django.core.cache import cache

from survey.models import UserFlags, SurveyUser, UserBanHistory
from survey.serializers import QuestionSerializer, TagSerializer, UserListSerializer, MetricSerializer
from survey.submodels.banner import Banner
from survey.submodels.metrics import Metric
from survey.submodels.survey import Question, SURVEY_STATUS_HAS_CONTRADICTING, SURVEY_STATUS_BOT
from survey.submodels.tag import Tag


from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from social_core.actions import do_complete
from social_django.utils import psa
from social_django.views import NAMESPACE, _do_login
from django.contrib.auth import REDIRECT_FIELD_NAME

from survey.subviews.auth import get_user, do_login
from survey.subviews.proof import check_proof

logger = logging.getLogger(__name__)


def index(request):
    context = {}

    ref_id = request.GET.get('ref_id')


    if request.method == 'POST':
        selected_language = request.POST.get('language-select')
        request.session['selected_language'] = selected_language

    current_language = request.session.get('selected_language')
    context['current_language'] = current_language

    user = request.user
    if ref_id:
        try:
            user = get_user(request, ref_id)
            do_login(request, user)
        except Exception as e:
            context['error'] = e

    return render(request, 'survey/index.html', context)


def login(request):
    request.session.flush()
    context = {
        'login': True
    }
    return render(request, 'survey/index.html', context)


def suspend(request):
    ban = UserBanHistory.is_blocked(request.user)

    if not ban:
        return redirect('/survey')

    suffixes = ['', 'st', 'nd', 'rd']

    count = UserBanHistory.objects.filter(user=request.user, date__gte=timezone.now()-timedelta(days=2)).count() + 1
    context = {
        'ban': ban,
        'ban_count': count,
        'ban_count_suffix': suffixes[count] if count < 4 else 'th'
    }
    return render(request, 'survey/error/suspend.html', context)


def manager(request):
    context = {}
    response = render(request, 'dashboard/index.html', context)
    response.set_cookie(CSRF_COOKIE_NAME, csrf.get_token(request))
    return response


@api_view(['POST', 'GET'])
def analytics(request):
    if request.GET.get('adblock') and request.user.is_authenticated:
        UserFlags.objects.create(user=request.user, key=UserFlags.ADBLOCK)

    user = request.user
    if request.method == 'POST' and request.user.is_authenticated and user.is_registered and request.data.get('fingerprint'):
        from survey.submodels.fingerprint import UserFingerprint
        fingerprint = request.data.get('fingerprint')
        UserFingerprint.add(user, fingerprint)

    check_proof(request)

    return JsonResponse({})


def banners(request):
    return JsonResponse(Banner.get_banner_set(), safe=False)


@never_cache
@csrf_exempt
@psa('{0}:complete'.format(NAMESPACE))
def complete(request, backend, *args, **kwargs):
    """Authentication complete view"""
    do_complete(request.backend, _do_login, user=None,
                       redirect_name=REDIRECT_FIELD_NAME, request=request,
                       *args, **kwargs)
    return redirect('/')


class QuestionsViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all().order_by('-id')
    search_fields = ('text', 'choice__text', 'tags__text')
    filter_backends = (SearchFilter,)
    serializer_class = QuestionSerializer
    permission_classes = (IsAdminUser, )


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().distinct('text')
    search_fields = ('text',)
    serializer_class = TagSerializer
    filter_backends = (SearchFilter,)
    permission_classes = (IsAdminUser, )


class UsersViewSet(viewsets.ModelViewSet):
    queryset = SurveyUser.objects.exclude(is_staff=True).exclude(provider__isnull=True).order_by('-id')
    search_fields = ('ref_id', 'provider__name', 'ip_history__ip', 'provider_user_id',)
    serializer_class = UserListSerializer
    filter_backends = (SearchFilter,)
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        qs = super(UsersViewSet, self).get_queryset()
        data = self.request.GET

        if data.get('blockedUsers') != 'true':
            qs = qs.exclude(is_active=False)

        if data.get('registeredUsers') == 'true':
            qs = qs.filter(social_auth__id__isnull=False).distinct()

        if data.get('activeLast24h') == 'true':
            qs = qs.filter(survey__created__gte=timezone.now() - timedelta(hours=24)).distinct()

        if data.get('onlyContradicting') == 'true':
            qs = qs.filter(survey__status=SURVEY_STATUS_HAS_CONTRADICTING).distinct()

        if data.get('onlyBots') == 'true':
            qs = qs.filter(survey__status=SURVEY_STATUS_BOT).distinct()

        qs = qs.annotate(survey_count=Count('survey'))

        order = data.get('ordering')
        if order:
            qs = qs.order_by(order)

        return qs
