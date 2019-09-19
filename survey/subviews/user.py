import logging
from datetime import timedelta

from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes

from django_server import settings
from django_server.utils import get_client_ip
from survey.models import USER_CAN_CHANGE_PROFILE_IN_DAY, SurveyUser
from survey.submodels.captcha import Recaptcha
from survey.submodels.survey import SURVEY_STATUS_HAS_CONTRADICTING, SURVEY_STATUS_BOT, SURVEY_STATUS_SUCCESS, \
    SURVEY_STATUS

logger = logging.getLogger(__name__)


@api_view(['GET', 'POST'])
@permission_classes([])
def profile(request):

    user = request.user
    if request.method == 'GET' and user.is_authenticated:
        all_networks = ['google-oauth2', 'facebook', 'vk-oauth2', 'discord', 'twitter', 'twitch']
        associated_networks = user.social_auth.all()
        associated_networks_names = [n.provider for n in associated_networks]
        not_associated_networks = [item for item in all_networks if item not in associated_networks_names]
        return render(request, 'survey/profile/index.html', {
            'associated_networks': associated_networks,
            'not_associated_networks': not_associated_networks if len(not_associated_networks) else None
        })

    data = request.data
    if not len(data):
        return JsonResponse({'success': False, 'error': 'No data'}, status=400)

    if user.is_authenticated and not user.can_update_data():
        return JsonResponse({'success': False, 'error': 'You can update profile only {} times in 24 hours'.format(
            USER_CAN_CHANGE_PROFILE_IN_DAY)}, status=403)

    try:
        user.update_data(data)
    except Exception as e:
        logger.error('[Profile] {}'.format(e))
        return JsonResponse({'success': False, 'error': str(e)}, status=403)

    return JsonResponse({'success': True})


@api_view(['POST'])
@permission_classes([])
def add_ref_id(request):
    user = request.user
    data = request.data

    try:
        user.set_ref_id(data.get('ref_id'))
    except Exception as e:
        logger.error('[Profile] {}'.format(e))
        return JsonResponse({'success': False, 'error': str(e)}, status=403)

    return JsonResponse({'success': True})


@api_view(['POST'])
@permission_classes([])
def feedback(request):
    user = request.user
    data = request.data
    ip = get_client_ip(request)

    if user.is_anonymous:
        return JsonResponse({'success': False, 'error': 'Please Login to leave feedback'}, status=400)

    if not Recaptcha.solve(data.get('captcha'), ip):
        return JsonResponse({'success': False, 'error': 'Wrong captcha!'}, status=400)

    if request.user.user_feedback.filter(type=data.get('type'), date__gte=timezone.now() - timedelta(hours=1)).order_by('-date').count() > 0:
        return JsonResponse({'success': False, 'error': 'You can leave feedback only once in a hour!'}, status=400)

    request.user.user_feedback.create(text=data.get('text'), fingerprint=data.get('fp'), type=data.get('type'))
    return JsonResponse({'success': True})


@api_view(['POST'])
@permission_classes([])
def bug_report(request):
    if request.method != 'POST':
        return redirect('/')

    user = request.user
    ip = get_client_ip(request)
    url = request.data.get('url') or ''
    email = request.data.get('email')
    message = request.data.get('message')
    fingerprint = request.data.get('fingerprint')
    is_feedback = request.GET.get('feedback')
    is_contacts = request.GET.get('contacts')

    if not Recaptcha.solve(request.data.get('captcha'), ip):
        return JsonResponse({'success': False, 'error': 'Wrong captcha!'}, status=400)

    template_name = "survey/emails/feedback_report.html" if is_feedback else "survey/emails/bug_report.html"
    from_email = settings.EMAIL_HOST_USER
    recipients = settings.EMAIL_RECIPIENTS

    context = {
        'ip': ip,
        'email': email if email else user.email,
        'partner_name': user.provider.name if (hasattr(user, 'provider') and user.is_authenticated) else '',
        'fingerprint': fingerprint,
        'message': message,
        'ref_id': user.ref_id,
        'user': user,
        'url': url,
        'registered': user.date_joined,
        'survey_done': user.survey_set.all().count(),
        'survey_valid': user.survey_set.filter(status=SURVEY_STATUS_SUCCESS).count(),
        'survey_bot': user.survey_set.filter(status=SURVEY_STATUS_BOT).count(),
        'survey_contradicting': user.survey_set.filter(status=SURVEY_STATUS_HAS_CONTRADICTING).count(),
        'survey_last_3': [SURVEY_STATUS[x.status][0] for x in user.survey_set.all().order_by('-id')[1:4]],
    }

    subject = 'Bug Report'
    if is_feedback:
        subject = 'Feedback'
    if is_contacts:
        subject = 'Contacts Page'

    subject = ('[{}] {}').format(subject, user)
    html_content = render_to_string(template_name, context)
    email = EmailMultiAlternatives(subject, html_content, from_email, recipients)
    email.attach_alternative(html_content, "text/html")
    email.send()
    print(html_content)

    print('[EMAIL] sent {} - {}'.format(subject, html_content))
    logger.info('[EMAIL] sent {} - {}'.format(subject, html_content))

    return JsonResponse({'success': True}, status=200)
