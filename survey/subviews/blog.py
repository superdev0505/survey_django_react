import logging

from django.shortcuts import render, redirect

from survey.submodels.blog import BlogPage
from survey.submodels.provider import Provider, PAYOUT_PROVIDER_BITCOIN, PAYOUT_USER_BITCOIN
from survey.models import SurveyUser
from survey.subviews.auth import do_login

logger = logging.getLogger(__name__)


def index(request):

    # Show Blog and articles only on specific domains
    if request.META['HTTP_HOST'] != 'moretvtime.com':
        return redirect('/')

    return render(request, 'survey/blog/index.html', {
        'blog_pages': BlogPage.objects.all()
    })


def page(request, id):

    # Show Blog and articles only on specific domains
    if request.META['HTTP_HOST'] != 'moretvtime.com':
        return redirect('/')

    return render(request, 'survey/blog/page.html', {
        'blog_page': BlogPage.objects.filter(id=id).first()
    })