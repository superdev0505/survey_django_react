from django.conf.urls import url
from django.urls import path
from django.views.generic import TemplateView

from dashboard import views
from dashboard.views import IndexView, AboutView, FaqView, ForgotPasswordView, MembersView, AddSiteView, SitesView, \
    PaymentView, StatisticsView, SupportView, WidgetsView, AddWidgetView, ContactManagerView, MessageView,\
    ProfileView, EditWidgetView,BannerView

app_name = 'dashboard'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('about', AboutView.as_view(), name='about'),
    path('faq', FaqView.as_view(), name='faq'),
    path('sign_up/<provider>/<providerUserId>', views.register, name='sign_up'),
    path('signin', views.signin, name='signin'),
    path('forgotpassword', ForgotPasswordView.as_view(), name='forgotpassword'),
    path('members', MembersView.as_view(), name='members'),
    path('payment', PaymentView.as_view(), name='payment'),
    path('statistics', StatisticsView.as_view(), name='statistics'),
    path('support', SupportView.as_view(), name='support'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('contactmanager', ContactManagerView.as_view(), name='contactmanager'),
    path('message/<id>', MessageView.as_view(), name='message'),
    path('sites', SitesView.as_view(), name='sites'),
    path('addsite', AddSiteView.as_view(), name='addsite'),
    path('widgets/<id>', WidgetsView.as_view(), name='widgets'),
    path('addwidget/<id>/<wid>', AddWidgetView.as_view(), name='addwidget'),
    path('editwidget/<id>/<wid>', EditWidgetView.as_view(), name='editwidget'),
    path('widget/addwidgetdata', views.add_widget_data_view),
    path('widget/getarticle', views.getarticle),
    url(r'^change_password$', views.change_password, name='change_password'),
    path('remove_items', views.remove_items, name="remove_sites"),
    path('remove_widget_items', views.remove_widget_items, name="remove_widget"),
    url(r'^logout/$', views.logout_view, name='logout'),
    path('404', TemplateView.as_view(template_name="dashboard/404.html"), name='404'),
    
    path('banner',views.BannerView, name='banner'),
]

