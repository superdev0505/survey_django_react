from django.contrib.sitemaps.views import sitemap
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from rest_framework import routers

from django_server.sitemaps import sitemaps
from survey.admin_views import FeedbackList, feedback_aggregated, SurveyList, SurveyAnswerList, ProvidersList, \
    MetricsList, user_block, report_countries, report_country_amounts
from survey.subviews import auth, user, blog, offerwall, external
from survey.subviews.survey import survey
from . import admin_views
from . import views

app_name = 'survey'

router = routers.DefaultRouter()
router.register('tags', views.TagsViewSet)
router.register('users', views.UsersViewSet),
router.register('questions', views.QuestionsViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('signup/', auth.signup_view, name='signup'),
    path('logout/', auth.logout_view, name='logout'),
    path('referer/', views.index, name='referer'),

    path('profile/', user.profile, name='profile'),
    path('add_ref/', user.add_ref_id, name='add_ref_id'),
    path('feedback/', user.feedback, name='feedback'),
    path('bug-report/', user.bug_report, name='bug_report'),

    path('analytics/', views.analytics, name='analytics'),
    path('banners/', views.banners, name='banners'),

    path('article/', survey.article, name='article'),
    path('article/<str:article>', survey.article, name='article_name'),
    path('survey/', survey.survey, name='survey'),
    path('vote/', survey.vote, name='vote'),

    path('offerwall/', offerwall.offerwall_help, name='offerwall_help'),
    path('offerwall/qr/', offerwall.offerwall_qr, name='offerwall_qr'),
    path('offerwall/profile/', offerwall.profile, name='offerwall_profile'),
    path('offerwall/<str:provider>', offerwall.offerwall_user, name='offerwall_provider'),
    path('offerwall/<str:provider>/<str:sub_id>', offerwall.offerwall_user, name='offerwall_user'),

    path('blog/', blog.index, name='blog'),
    path('blog/<int:id>', blog.page, name='blog_page'),

    path('privacy/', TemplateView.as_view(template_name='survey/privacy.html'), name='privacy'),
    path('contacts/', TemplateView.as_view(template_name='survey/contacts.html'), name='contacts'),
    path('cookie/', TemplateView.as_view(template_name='survey/cookie.html'), name='cookie'),

    path('external/postback', external.external_postback, name='external_postback'),

    path('error/referer/', TemplateView.as_view(template_name='survey/error/referer.html'), name='error_referer'),
    path('error/vpn/', TemplateView.as_view(template_name='survey/error/vpn.html'), name='error_vpn'),
    path('error/ban/', TemplateView.as_view(template_name='survey/error/ban.html'), name='error_ban'),
    path('error/suspend/', views.suspend, name='error_suspend'),

    path('api/user/login', admin_views.user_login, name='user_login'),
    path('api/user/logout', admin_views.user_logout, name='user_logout'),
    path('api/user/profile', admin_views.user_profile, name='user_profile'),

    path('api/report/countries', report_countries, name='report_countries'),
    path('api/report/country_amounts', report_country_amounts, name='report_country_amounts'),
    path('api/user/feedback_list', FeedbackList.as_view(), name='feedback_list'),
    path('api/user/feedback_list_aggregated', feedback_aggregated, name='feedback_aggregated'),
    path('api/user/survey', SurveyList.as_view(), name='user_survey_list'),
    path('api/user/survey/answers', SurveyAnswerList.as_view(), name='user_survey_answers'),

    path('api/user/block/', user_block, name='user_block'),

    path('api/providers', ProvidersList.as_view(), name='providers'),
    path('api/metrics', admin_views.metrics, name='metrics'),
    path('api/metrics/chart', MetricsList.as_view(), name='metrics_chart'),

    path('api/user/blockhistory', MetricsList.as_view(), name='metrics_chart'),

    path('api/tags/add', admin_views.tags_add, name='tags_add'),
    path('api/answer_types', admin_views.answer_types, name='answer_types'),
    path('api/questions/save', admin_views.question_save, name='questions_save'),
    path('api/questions/delete', admin_views.question_delete, name='questions_delete'),
    path('api/provider/test/<str:provider>', admin_views.provider_test, name='provider_test'),
    path('api/', include(router.urls)),

    # Admin / cms
    re_path('manager/.*', views.manager, name='manager'),

    # test pages
    re_path('js-test', TemplateView.as_view(template_name='js-test.html'), name='js-test'),


    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
]
