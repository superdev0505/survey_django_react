import csv
import traceback
from datetime import timedelta

from django.contrib.auth import authenticate, login, logout
from django.core import management
from django.core.signing import JSONSerializer
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.template.context_processors import csrf
from django.utils import timezone
from django.utils.six import StringIO
from django.views.decorators.csrf import csrf_exempt
from django_countries.serializer_fields import CountryField
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from django_server import db, settings
from django_server.utils import cmd_execute
from survey.countries import COUNTRIES, COUNTRY_CODES
from survey.models import SurveyUser, UserFeedback
from survey.pagination import LargeResultsSetPagination
from survey.submodels.metrics import Metric
from survey.submodels.provider import Provider
from survey.submodels.survey import ANSWER_TYPES, Question, Choice, Survey, QuestionAnswer, SURVEY_STATUS, ANSWER_VOTE, \
    SURVEY_STATUS_SUCCESS
from survey.submodels.tag import Tag
from survey.serializers import QuestionSerializer, TagSerializer, UserSerializer, UserListSerializer, \
    UserFeedbackSerializer, SurveySerializer, QuestionAnswerSerializer, UserAdminSerializer, ProviderSerializer, \
    MetricSerializer


@api_view(['GET'])
def user_profile(request):
    csrf(request)
    return Response(UserSerializer(request.user).data)


@api_view(['POST'])
def user_login(request):
    username = request.data.get('login', '')
    password = request.data.get('password', '')
    user = authenticate(username=username, password=password)

    if user:
        login(request, user)
        serializer = UserSerializer(user)
        return JsonResponse(serializer.data)
    else:
        return JsonResponse({"status": "error"})


@api_view(['POST'])
def user_logout(request):
    logout(request)
    request.session.flush()
    return Response({"status": "logout"})


@api_view(['POST'])
def user_block(request):
    user = request.data.get('id')

    user = SurveyUser.objects.get(id=user)
    user.is_active = not user.is_active
    user.save()

    return JsonResponse({'success': True})


@api_view(['POST', 'GET'])
def metrics(request):
    sql = '''
    with 
         pre_txn as (
             select amount, survey_id, provider_id
             from survey_providertransaction
             union all
             select amount, survey_id, ss.provider_id
               from survey_usertransaction 
               join survey_surveyuser ss on survey_usertransaction.user_id = ss.id
         ),
         txn as (
             select survey_id, provider_id, sum(amount) as amount
             from pre_txn
             group by survey_id, provider_id
         ),
         survey as (
             select TO_CHAR(created, 'dd/mm/yyyy') as trdate,
                    case
                        when status = 0 then 1 when status != 0 then 0 end                        as started,
                    case
                        when status = 1 then 1 when status != 1 then 0 end                        as success,
                    case
                        when status = 2 then 1 when status != 2 then 0 end                        as is_contradicting,
                    case
                        when status = 3 then 1 when status != 3 then 0 end                        as is_changing_ip,
                    case
                        when status = 4 then 1 when status != 4 then 0 end                        as is_often,
                    case
                        when status = 5 then 1 when status != 5 then 0 end                        as is_zombie,
                    case
                        when status = 6 then 1 when status != 6 then 0 end                        as is_bot,
                    case
                        when status in (0, 1) then 0 when status not in (0, 1) then 1 end         as failed,
                    ss.provider_id,
                    su.status,
                    su.id,
                    su.user_id,
                    txn.amount,
                    su.id
              from survey_survey su
              full join txn on su.id = txn.survey_id
              join survey_surveyuser ss
                on su.user_id = ss.id
             where su.created is not null
             order by created desc
         ),
         all_txn as (
             select trdate {GROUP_CAUSE},
                    count(*)     as "all",
                    sum(started) as started,
                    sum(success) as success,
                    sum(is_contradicting) as is_contradicting,
                    sum(is_changing_ip) as is_changing_ip,
                    sum(is_often) as is_often,
                    sum(is_bot) as is_bot,
                    sum(is_zombie)  as is_zombie,
                    sum(failed)  as failed,
                    sum(amount)
             from survey ss
             group by trdate {GROUP_CAUSE}
         )
    select TO_DATE(txn.trdate, 'DD/MM/YYYY') as date, txn.* {GROUP_CAUSE} {SELECT_CAUSE}
      from all_txn txn
      {JOIN_CAUSE}
      {WHERE_CAUSE}
     order by date desc;
    '''

    params = []
    group_cause = ''
    where_cause = ''
    join_cause = ''
    select_cause = ''

    date = request.data.get('date')
    provider = request.data.get('provider')

    if provider:
        params.append(int(provider))
        select_cause = ', pr.name as provider_name'
        join_cause = 'join survey_provider pr on pr.id = txn.provider_id'
        where_cause = 'where txn.provider_id=%s'
        group_cause = ', provider_id'
        if date:
            params.append(str.replace(date, '-', '/'))
            where_cause = where_cause + ' and txn.trdate=%s'
    elif date:
        select_cause = ', pr.name as provider_name'
        join_cause = 'join survey_provider pr on pr.id = txn.provider_id'
        where_cause = 'where txn.trdate=%s'
        group_cause = ', provider_id'
        params.append(str.replace(date, '-', '/'))

    return JsonResponse(db.fetch_all(sql.format(
        GROUP_CAUSE=group_cause,
        WHERE_CAUSE=where_cause,
        JOIN_CAUSE=join_cause,
        SELECT_CAUSE=select_cause
    ), params=params), safe=False)


class MetricsList(generics.ListAPIView):
    permission_classes = (IsAdminUser,)
    queryset = Metric.objects.all()
    serializer_class = MetricSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(date__gte=timezone.now() - timedelta(days=7)).order_by('-date')
        serializer = MetricSerializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)


class ProvidersList(generics.ListAPIView):
    permission_classes = (IsAdminUser,)
    pagination_class = None
    queryset = Provider.objects.all().order_by('name')
    serializer_class = ProviderSerializer


class FeedbackList(generics.ListAPIView):
    permission_classes = (IsAdminUser,)
    queryset = UserFeedback.objects.all().order_by('-date')
    serializer_class = UserFeedbackSerializer


class SurveyList(generics.ListAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = (IsAdminUser,)

    def list(self, request, *args, **kwargs):
        # Note the use of `get_queryset()` instead of `self.queryset`
        user = SurveyUser.objects.get(id=request.GET.get('user_id'))
        queryset = self.get_queryset().filter(user=user).order_by('-id')
        serializer = SurveySerializer(queryset, many=True)
        return JsonResponse({
            'data': serializer.data,
            'user': UserAdminSerializer(user).data,
            'status': SURVEY_STATUS
        })


class SurveyAnswerList(generics.ListAPIView):
    queryset = QuestionAnswer.objects.all()
    serializer_class = QuestionAnswerSerializer
    permission_classes = (IsAdminUser,)

    def list(self, request, *args, **kwargs):
        # Note the use of `get_queryset()` instead of `self.queryset`
        survey = Survey.objects.get(id=request.GET.get('survey_id'))
        user = survey.user

        queryset = self.get_queryset().filter(survey=survey).order_by('-id')
        serializer = QuestionAnswerSerializer(queryset, many=True)
        return JsonResponse({
            'data': serializer.data,
            'user': UserAdminSerializer(user).data
        })


@api_view(['POST'])
def report_countries(request):
    sql = '''
            with countries as (
            select * from (values {}) as t(name, ordering)
         ),
         survey as (
            select su.country,
                   case when ss.device = 0 then 1 else 0 end mobile,
                   case when ss.device = 1 then 1 else 0 end desktop
            from survey_questionanswer qa
                     join survey_survey ss on ss.id = qa.survey_id
                     join survey_surveyuser su on ss.user_id = su.id
            where ss.status = 1
              and ss.created >= TO_TIMESTAMP(%s, 'dd/mm/yyyy HH24:MI:SS')
              and ss.created <= TO_TIMESTAMP(%s, 'dd/mm/yyyy HH24:MI:SS')
        ),
        data as (
            select country, sum(mobile) mobile,  sum(desktop) desktop
            from survey
            group by country
        )
    select countries.name, d.mobile, d.desktop
      from countries
      left join data d on countries.name = d.country
      order by countries.ordering'''

    countries = []
    lines = str.split(request.data.get('countries'),'\n')
    for i in range(len(lines)):
        country = COUNTRIES.get(lines[i])
        countries.append("('{}',{})".format(country, i + 1))
    countries = ','.join(countries)
    sql = sql.format(countries)

    date_from = request.data.get('date_from') + ' 00:00:00'
    date_to = request.data.get('date_to') + ' 23:59:59'

    data = db.fetch_all_flat(sql, [date_from, date_to])

    return JsonResponse([[COUNTRY_CODES.get(x[0]), x[1] or 0, x[2] or 0] for x in data], safe=False)


@api_view(['GET'])
def report_country_amounts(request):
    sql = '''
            with data as (
                select date_created, device, amount, survey_id, sp.provider_id, ss2.country
                from survey_providertransaction sp
                     join survey_survey s on sp.survey_id = s.id
                     join survey_surveyuser ss2 on s.user_id = ss2.id
                where date_created >= TO_TIMESTAMP(%s, 'dd/mm/yyyy HH24:MI:SS')
                  and date_created <= TO_TIMESTAMP(%s, 'dd/mm/yyyy HH24:MI:SS')
                union all
                select date_created, ss1.device, amount, survey_id, ss.provider_id, ss.country
                from survey_usertransaction
                    join survey_survey ss1 on survey_usertransaction.survey_id = ss1.id
                     join survey_surveyuser ss on survey_usertransaction.user_id = ss.id
                where date_created >= TO_TIMESTAMP(%s, 'dd/mm/yyyy HH24:MI:SS')
                  and date_created <= TO_TIMESTAMP(%s, 'dd/mm/yyyy HH24:MI:SS')
            ),
                turn_data as (
                    select TO_CHAR(date_created, 'yyyy-mm-dd') as trdate,
                        case when device = 0 then amount else 0 end mobile,
                        case when device = 1 then amount else 0 end desktop,
                        country
                    from data
                )
              select trdate,
                     country,
                     sum(mobile) mobile,
                     sum(desktop) desktop
                from turn_data
                group by trdate, country
                order by trdate desc, country
            '''

    date_from = request.GET.get('date_from') + ' 00:00:00'
    date_to = request.GET.get('date_to') + ' 23:59:59'

    data = db.fetch_all_flat(sql, [date_from, date_to, date_from, date_to])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="report.csv"'
    writer = csv.writer(response)
    for x in data:
        writer.writerow([x[0], COUNTRY_CODES.get(x[1]), x[2] or 0, x[3] or 0])

    return JsonResponse([[x[0], COUNTRY_CODES.get(x[1]), x[2] or 0, x[3] or 0] for x in data], safe=False)


@api_view(['GET'])
def report_countries(request):
    sql = ''''''

    countries = []
    lines = str.split(request.data.get('countries'),'\n')
    for i in range(len(lines)):
        country = COUNTRIES.get(lines[i])
        countries.append("('{}',{})".format(country, i + 1))
    countries = ','.join(countries)
    sql = sql.format(countries)

    date_from = request.data.get('date_from') + ' 00:00:00'
    date_to = request.data.get('date_to') + ' 23:59:59'

    data = db.fetch_all_flat(sql, [date_from, date_to])

    return JsonResponse([[COUNTRY_CODES.get(x[0]), x[1] or 0, x[2] or 0] for x in data], safe=False)



@api_view(['GET'])
def feedback_aggregated(request):
    sql = '''with flags as (
                select TO_CHAR(date, 'dd/mm/yyyy') as trdate,
                       fl.key,
                       count(fl.key) cnt
                from survey_userflags fl
                group by trdate, fl.key
            ), feedbacks as (
                select TO_CHAR(date, 'dd/mm/yyyy') as trdate,
                       fe.type,
                       count(fe.type) cnt
                from survey_userfeedback fe
                group by trdate, fe.type
            ), united as (
                select fl.*
                from flags fl
                union all
                select *
                from feedbacks
            ), aggregated as (
                select
                       trdate,
                       case when u.key = 'ADBLOCK' then cnt else 0 end as blocked_adblock,
                       case when u.key = 'VPN' then cnt else 0 end as blocked_vpn,
                       case when u.key = 'vpn' then cnt else 0 end as feedback_adblock,
                       case when u.key = 'adblock' then cnt else 0 end as feedback_vpn
                from united u
            )
            select trdate as date, sum(blocked_adblock)blocked_adblock, sum(blocked_vpn)blocked_vpn, sum(feedback_adblock)feedback_adblock, sum(feedback_vpn)feedback_vpn
             from aggregated group by trdate order by trdate desc '''

    return JsonResponse(db.fetch_all(sql), safe=False)


@api_view(['GET'])
def answer_types(request):
    return Response(ANSWER_TYPES)


@api_view(['POST'])
def tags_add(request):
    tag_text = request.data.get('text')

    tag, created = Tag.objects.get_or_create(text=tag_text)
    return Response(TagSerializer(tag).data)


@api_view(['POST'])
def question_save(request):
    q = request.data
    id = q.get('id')
    text = q.get('text')
    tags = q.get('tags')
    enabled = q.get('enabled')
    choice_set = q.get('choice_set')
    answer_type = q.get('answer_type')

    # Vote can have only two answers
    if answer_type == ANSWER_VOTE and len(choice_set) != 2:
        return JsonResponse({'error': 'Question type Vote should have two Answers'})

    question = do_question_save(text, answer_type=answer_type, enabled=enabled, id=id, tags=tags, choice_set=choice_set)

    return Response(QuestionSerializer(question).data)


def do_question_save(text, answer_type=ANSWER_VOTE, enabled=False, id=None, tags=[], choice_set=[], ):

    # Find question and update primitive fields for it
    question = Question.objects.filter(id=id).first() if id else Question()
    question.text = text
    question.enabled = enabled
    question.answer_type = answer_type
    question.save()

    # Update Question tags
    question_tags = []
    for t in tags:
        tid = t.get('id')
        tag = Tag.objects.filter(id=tid).first() if tid else Tag.objects.create(text=t.get('text'))
        question_tags.append(tag)
    question.tags.set(question_tags)

    # Then iterate over it's choices
    for c in choice_set:
        cid = c.get('id')
        choice = Choice.objects.filter(id=cid).first() if cid else Choice()
        choice.text = c.get('text')
        choice.question = question
        choice.save()

        if choice.text == '':
            choice.delete()
            continue

        choice_tags = []
        for t in c.get('tags', []):
            ctid = t.get('id')
            tag = Tag.objects.filter(id=ctid).first() if ctid else Tag.objects.create(text=t.get('text'))
            choice_tags.append(tag)
        choice.tags.set(choice_tags)

    return question


@api_view(['DELETE'])
def question_delete(request):
    q = request.data
    id = q.get('id')
    question = Question.objects.filter(id=id).first()
    if question:
        question.delete()
    return Response({})


def provider_test(request, provider):
    if request.user.is_anonymous or (not request.user.is_staff):
        return render(request, 'survey/components/log.html', {
            'log': 'Staff only'
        })

    provider = Provider.objects.filter(name=provider).first()
    if not provider:
        return render(request, 'survey/components/log.html', {
            'log': 'Wrong Provider'
        })

    # TODO Make Validators
    user = request.GET.get('user', '')
    btc = request.GET.get('btc', '')
    ip = request.GET.get('ip', '')

    cmd = 'sh {} -p {}'
    path = '/var/www/survey/scripts/provider_test.sh'
    if settings.DEBUG:
        path = '/Users/vankyver/project/up/MingleCash/survey/scripts/provider_test.sh'

    cmd = cmd.format(path, provider)
    if user:
        cmd = '{} -u {}'.format(cmd, user)
    if btc:
        cmd = '{} -b {}'.format(cmd, btc)
    if ip:
        cmd = '{} -ip {}'.format(cmd, ip)

    output = cmd_execute(cmd)

    return render(request, 'survey/components/log.html', {
        'log': output
    })

