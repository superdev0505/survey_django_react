import logging
from django.views.generic import TemplateView

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from dashboard.forms import *
from django.shortcuts import render
from dashboard.models import Banners, BannerSize
from django.core import serializers
import hashlib
import random
import string
from django.contrib.auth.models import User
import uuid
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from datetime import datetime, timedelta, time
from django.db import models
from django.db.models import Func
from django.db.models import Sum
from django.contrib.auth import logout
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from survey.models import SurveyUser
from django.core.mail import EmailMultiAlternatives
from survey.submodels.provider import Provider
import dateutil.relativedelta
import calendar,inflect,time

logger = logging.getLogger(__name__)


def logredirect():
    login_url = 'login'
    redirect_field_name = 'login'


class IndexView(TemplateView):
    template_name = 'dashboard/index.html'


class AboutView(TemplateView):
    template_name = 'dashboard/pages/about.html'

    def get_context_data(self):
        context = super(AboutView, self).get_context_data()
        page = Page.objects.filter(pagerole='about').values()
        logger.info('[AboutView] Request - {0}'.format(str('page')))
        if page:
            context['PageData'] = page
        else:
            logger.error('[AboutView] no pages')

        return context


class FaqView(TemplateView):
    template_name = 'dashboard/pages/faq.html'

    def get_context_data(self):
        context = super(FaqView, self).get_context_data()
        page = Page.objects.filter(pagerole='faq').values()
        logger.info('[FaqView] Request - {0}'.format(str('page')))
        if page:
            context['PageData'] = page
        else:
            logger.error('[FaqView] no pages')
        return context


def register(request, provider, providerUserId):    
    register = False  
    http_host=request.META['HTTP_HOST']
    if request.method == 'POST':  	
        form = SignUpForm(request.POST)        
        if form.is_valid(): 
            r = form.save(commit=False)  
            r.is_active = True
            provider=Provider.objects.filter(name=provider).first()                        
            print("provider id=",provider) 
            # providerVal=provider.name

            r.provider=provider            
            r.provider_user_id=providerUserId
            r.save()        
            SurveyUser.objects.filter(id=r.id).update(username=uuid.uuid4().hex[:30])
            user = SurveyUser.objects.filter(id=r.id).first()
            logger.info('[register] Request - {0}'.format(str('register')))
            register = True   
            # text_content = 'Account Activation Email'
            # subject = 'Email Activation'
            # template_name = "dashboard/members/activation.html"
            # from_email = settings.EMAIL_HOST_USER
            # recipients = [request.POST.get('email')]
            # kwargs = {
            #     "uidb64": user.pk,
            #     "token": default_token_generator.make_token(user)
            # }
            # activation_url = "/account/activate?u={0}&token={1}".format(user.pk, default_token_generator.make_token(user))  #reverse("app:activate_user_account", kwargs=kwargs)
            # activate_url = "{0}://{1}{2}".format(request.scheme, request.get_host(), activation_url)   
            # context = {
            #     'user': user,
            #     'activate_url': activate_url
            # }
            # html_content = render_to_string(template_name, context)
            # email = EmailMultiAlternatives(subject, text_content, from_email, recipients)
            # email.attach_alternative(html_content, "text/html")
            # email.send()


    else:        
        form = SignUpForm()
    return render(request, 'dashboard/pages/signup.html', {'form': form, 'register': register})


def activate_user_account(request):
    try:
        uid = request.GET.get("u")
        user = SurveyUser.objects.get(pk=uid)        
    except SurveyUser.DoesNotExist:
        user = None

    token = request.GET.get("token")   
    if user and default_token_generator.check_token(user, token):
        user.is_email_verified = True
        user.is_active = True
        user.save()    
        # message="Your Account has been activated. Click Here For Login"  +  '<a href="/dashboard/signin"> Click Here </a>' 

    return render(request, 'dashboard/pages/account_activate.html')


def signin(request):
    template_name = 'dashboard/pages/signin.html'
    context = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')       
        usr = SurveyUser.objects.filter(email=email).first()  
        
        if usr:            
            if usr.is_active == False:
                context['error'] = "Your account has not been verified, Please check your email and verify your email address"
                return render(request, template_name, context)

            user = authenticate(username=usr.username, password=password)
            if not user:                
                context['error'] = "Wrong Username or Password"
            else:
                login(request, user)
                return HttpResponseRedirect('members')
        else:
            context['error'] = "Wrong Username or Password"

    else:
        logger.error('[Signin ] Wrong request method')

    return render(request, template_name, context)


class ForgotPasswordView(TemplateView):
    template_name = 'dashboard/pages/forgotpassword.html'
    

class MembersView(LoginRequiredMixin, TemplateView):
    logredirect()
    template_name = 'dashboard/members_index.html'   

    def get_context_data(self):  
        request = self.request
        context = super(MembersView, self).get_context_data()
        today = datetime.now().date()           
        yesterday = datetime.now().date() - timedelta(1)  
        user=request.user 
        site = Site.objects.filter(user=request.user)       
        all_sites = [y.id for y in site]  

        todayDate = datetime.now()
        if todayDate.day > 25:
            todayDate += timedelta(7)
        
        previous_month_start_date = todayDate.replace(day=1)
        days_list = [] 
        days_dict = dict()

        last_day_of_month=calendar.monthrange(today.year,today.month)               
        
        for dates in range(1,last_day_of_month[-1]+1):            
            days_list.append(dates)
            if dates not in days_dict:
                days_dict[dates] = 0    
                      
        if site:
            widget = Widget.objects.filter(site__in=all_sites)
            all_widget = [y.wid for y in widget]
            rfcompany_today = DashboardCompany.objects.filter(companyname__in=all_widget, date=today) \
                .annotate(m=Month('date')) \
                .values('m') \
                .annotate(total=Sum('bannerloads')) \
                .order_by()
            rfcompany_yesterday = DashboardCompany.objects.filter(companyname__in=all_widget, date=yesterday) \
                .annotate(m=Month('date')) \
                .values('m') \
                .annotate(total=Sum('bannerloads')) \
                .order_by()

            revenu_today = Revenue.objects.filter(companyname__in=all_widget, date=today) \
                .values('date') \
                .annotate(totalmoney=Sum('totalmoney')) \
                .order_by('-date')

            revenu_yesterday = Revenue.objects.filter(companyname__in=all_widget, date=yesterday) \
                .values('date') \
                .annotate(totalmoney=Sum('totalmoney')) \
                .order_by('-date')

            if rfcompany_today:
                for s in rfcompany_today:
                    context['today'] = s['total']
            else:
                context['today'] = 0

            if rfcompany_yesterday:
                for s in rfcompany_yesterday:
                    context['yesterday'] = s['total']
            else:
                context['yesterday'] = 0

            if revenu_today:
                for s in revenu_today:
                    context['r_today'] = s['totalmoney']
            else:
                context['r_today'] = 0

            if revenu_yesterday:
                for s in revenu_yesterday:
                    context['r_yesterday'] = s['totalmoney']
            else:
                context['r_yesterday'] = 0
            revenu_previous_month = Revenue.objects.filter(companyname__in=all_widget, 
                date__range=[previous_month_start_date, today]) \
            .values('date','totalmoney')\
            .annotate(totalRevenue=Sum('totalmoney'))\
            .order_by('date')    

            days_list_with_data = [] 
            revenue_list_with_data=[] 
            days_list_ordinal=[]

            if revenu_previous_month:
                for data in revenu_previous_month:
                    days=data['date'].day  
                    days_list_with_data.append(days)
                    context['total']=data['totalRevenue'] 
                    days_dict[days] = context['total']   

            for key, val in days_dict.items():
                revenue_list_with_data.append(val)
                
            ordinals = inflect.engine()
            for i in range(1,len(days_list)+1):
                ordinal_day=ordinals.ordinal(i) 
                days_list_ordinal.append(ordinal_day)  
            
            chart_month = ''#time.strftime('%B', time.struct_time((0, today.month, 0,)+(0,)*6))
            context['revenue_list_with_data'] = revenue_list_with_data 
            context['days_list']=days_list
            context['chart_month']=chart_month
            context['days_list_ordinal']=days_list_ordinal
            return context


class AddSiteView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/members/addsite.html'

    def post(self, request, *args, **kwargs):
        Site(
            # name=request.POST['name'],
            webaddress=request.POST['webaddress'],
            # websitelanguage=request.POST['websitelanguage'],
            # websitetraffic=request.POST['websitetraffic'],
            site_status='Approved',
            user=request.user
        ).save()
        logger.info('[AddSiteView] Request - {0}'.format(str('site')))
        return HttpResponseRedirect('sites')


class PaymentView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/members/payment.html'

    def post(self, request, *args, **kwargs):
        context = {}
        email = request.user.email       
        password = request.POST.get('password')       
        usr = SurveyUser.objects.filter(email=email).first()
        user = authenticate(username=usr.username, password=password)
        if not user: 
            context['status'] = "Invalid User"
        else:
            if user is not None:
                if user.is_active:
                    type = request.POST.get('type')
                    if type == 'paypal':
                        Paypal(
                            type=request.POST.get('type'),                            
                            paymentthreshold=request.POST.get('paymentthreshold'),
                            paypalemail=request.POST.get('paypalemail'),                           
                            user=request.user,
                        ).save()
                        context['status'] = "Paypal Informtion updated"                       
                        logger.info('[ProfileView] Request - {0}'.format(str('paypal')))
                    elif type == 'webmoney':
                        Webmoney(
                            type=request.POST.get('type'),                           
                            paymentthreshold=request.POST.get('paymentthreshold'),
                            wmz=request.POST.get('wmz'),
                            user=request.user,
                        ).save()
                        context['status'] = "Webmoney Informtion updated"
                        logger.info('[ProfileView] Request - {0}'.format(str('webmoney')))

                    elif type == 'Epayment':
                        Epayment(
                            type=request.POST.get('type'),
                            paymentthreshold=request.POST.get('paymentthreshold'),
                            ewallet=request.POST.get('ewallet'),
                            user=request.user,
                        ).save()
                        context['status'] = "Epayment Informtion updated"
                        logger.info('[ProfileView] Request - {0}'.format(str('Payoneer')))

                    elif type == 'Payoneer':
                        Payoneer(
                            type=request.POST.get('type'),
                            paymentthreshold=request.POST.get('paymentthreshold'),                           
                            paypalemail=request.POST.get('paypalemail'),
                            user=request.user,
                        ).save()
                        context['status'] = "Payoneer Informtion updated"
                        logger.info('[ProfileView] Request - {0}'.format(str('Payoneer')))

        return render(request, self.template_name, context)

    # def get_context_data(self):
    #     request = self.request
    #     context = super(PaymentView, self).get_context_data()
    #     payment = Payment.objects.filter(user=request.user).values()
    #     logger.info('[SitesSupportViewView] Request - {0}'.format(str('payment')))
    #     if payment:
    #         context['PaymentView'] = payment
    #     else:
    #         logger.error('[PaymentView] no data')
    #     return context


class SupportView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/members/support.html'

    def get_context_data(self):
        request = self.request
        context = super(SupportView, self).get_context_data()
        support = Support.objects.filter(user=request.user).values()
        logger.info('[SitesSupportViewView] Request - {0}'.format(str('support')))
        if support:
            context['SupportView'] = support
        else:
            logger.error('[SupportView] no data')

        return context


class SitesView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/members/sites.html'

    def get_context_data(self):
        request = self.request
        context = super(SitesView, self).get_context_data()
        site = Site.objects.filter(user=request.user).values()
        logger.info('[SitesView] Request - {0}'.format(str('site')))
        if site:
            context['SiteData'] = site
        else:
            logger.error('[SiteData] no data')

        return context


def remove_items(request):
    if request.method == 'POST':
        item_id = int(request.POST.get('item_id'))
        if item_id:
            item = Site.objects.get(id=item_id)
            item.delete()
            logger.info('have item id' + str(item_id))
            return HttpResponseRedirect('sites')
        else:
            logger.error('does have item id')
    else:
        logger.error('Problem when post data')


class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/members/statistics.html'

    def get_context_data(self):
        request = self.request
        context = super(StatisticsView, self).get_context_data()
        site = Site.objects.filter(user=request.user)        
        if site:
            all_sites = [y.id for y in site]
            widget = Widget.objects.filter(site__in=all_sites)
            all_widget = [y.wid for y in widget] 

            referrercompany = RfCompany.objects.filter(companyname__in=all_widget) \
                .values('date') \
                .annotate(bannerloads=Sum('bannerloads'), clicks=Sum('clicks')) \
                .order_by('-date')
              
            rfcompany_total = RfCompany.objects.filter(companyname__in=all_widget) \
                .aggregate(bannerloads=Sum('bannerloads'), clicks=Sum('clicks'))
               
            if rfcompany_total:
                context['totaldata'] = rfcompany_total

            revenu_total_t = Revenue.objects.filter(companyname__in=all_widget) \
                .aggregate(totalmoney=Sum('totalmoney'))
           
            revenu_total = Revenue.objects.filter(companyname__in=all_widget) \
                .values('date') \
                .annotate(totalmoney=Sum('totalmoney')) \
                .order_by('-date')   
            
            for idx, item in enumerate(referrercompany):
                revenu_total = revenu_total.filter(date__contains=item['date'])
                if not revenu_total:
                    referrercompany[idx]['totalmoney'] = 0
                else:
                    referrercompany[idx]['totalmoney'] = revenu_total[0]['totalmoney']


            context['rdata'] = referrercompany
            context['revenu'] = revenu_total

            context['totalmoney'] = revenu_total_t
            context['from'] = datetime.now().date().strftime("%d.%m.%Y")
            context['widget'] = widget
            context['allsite'] = site
            context['till'] = (datetime.now().date() - timedelta(2)).strftime("%d.%m.%Y")
            logger.info('[StatisticsView] Request - {0}'.format(str('referrercompany')))

        return context

    def post(self, request, *args, **kwargs):
        context = {}
        site_p = request.POST.get('site')
        widget_p = request.POST.get('widget')
        frm = request.POST.get('from')
        till = request.POST.get('till')
        if frm:
            format_str = '%d.%m.%Y'  # The format
            datetime_frm = datetime.strptime(frm, format_str)
            frm_qs = datetime_frm.date()
        else:
            frm_qs = datetime.now().date().strftime("%d.%m.%Y")

        if till:
            format_str = '%d.%m.%Y'  # The format
            datetime_till = datetime.strptime(till, format_str)
            till_qs = datetime_till.date()
        else:
            till_qs = (datetime.now().date() - timedelta(2)).strftime("%d.%m.%Y")

        # print(widget_p)
        # created__lte=today_end, created__gte=today_start,
        if site_p == "0":
            site = Site.objects.filter(user=request.user)

        else:
            site = Site.objects.filter(id=int(site_p))

        all_sites = [y.id for y in site]
        if site:
            if widget_p == "0":
                widget = Widget.objects.filter(site__in=all_sites)
            else:
                widget = Widget.objects.filter(wid=widget_p)

            all_widget = [y.wid for y in widget]

            # print(all_widget)
            referrercompany = RfCompany.objects.filter(companyname__in=all_widget, created__lte=till_qs,
                                                       created__gte=frm_qs) \
                .values('date') \
                .annotate(bannerloads=Sum('bannerloads'), clicks=Sum('clicks')) \
                .order_by('-date')

            rfcompany_total = RfCompany.objects.filter(companyname__in=all_widget, created__lte=till_qs,
                                                       created__gte=frm_qs) \
                .aggregate(bannerloads=Sum('bannerloads'), clicks=Sum('clicks'))

            if rfcompany_total:
                context['totaldata'] = rfcompany_total

            revenu_total_t = Revenue.objects.filter(companyname__in=all_widget, created__lte=till_qs,
                                                    created__gte=frm_qs) \
                .aggregate(totalmoney=Sum('totalmoney'))

            revenu_total = Revenue.objects.filter(companyname__in=all_widget, created__lte=till_qs, created__gte=frm_qs) \
                .values('date') \
                .annotate(totalmoney=Sum('totalmoney')) \
                .order_by('-date')

            for idx, item in enumerate(referrercompany):
                revenu_total = revenu_total.filter(date__contains=item['date'])
                if not revenu_total:
                    referrercompany[idx]['totalmoney'] = 0
                else:
                    referrercompany[idx]['totalmoney'] = revenu_total[0]['totalmoney']
            # print(referrercompany)
            # print(rfcompany_total)
            context['revenu'] = revenu_total
            context['totalmoney'] = revenu_total_t
            context['rdata'] = referrercompany

            context['from'] = datetime.now().date().strftime("%d.%m.%Y")
            s_p = Site.objects.filter(user=request.user)
            all_sites = [y.id for y in s_p]
            w_p = Widget.objects.filter(site__in=all_sites)
            context['allsite'] = s_p
            context['widget'] = w_p
            context['till'] = (datetime.now().date() - timedelta(2)).strftime("%d.%m.%Y")
            logger.info('[StatisticsView] Request - {0}'.format(str('referrercompany')))

        return render(request, self.template_name, context)


class WidgetsView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/members/widgets.html'

    def get_context_data(self, id):
        print('inside view')
        
        context = super(WidgetsView, self).get_context_data()
        context['message'] = ""    
        # widget = Widget.objects.filter(site=id).values()
        # logger.info('[AddWidgetView] Request - {0}'.format(str('widget')))
        # context['WidgetID'] = id
        # if widget:
        #     context['WidgetData'] = widget
        # else:
        #     logger.error('[WidgetData] no data')

        return context
    
    def post(self, request, *args, **kwargs):
        print('inside view Post')
        context = {}
        paid_type = request.POST.get("paid-type") # YES OR NO
        post_back_url = request.POST.get("post_back_url")
        user_id = request.POST.get("user_id")
        reward = request.POST.get("reward")
        faucethub_email = request.POST.get("faucethub_email")
        if request.POST.get("pay_type_radio") == "PAYPAL":
            try:              
                Paypal(
                        type=request.POST.get('type'),                            
                        paypalemail=request.POST.get('paypalemail'),                           
                        user=request.user,
                    ).save()    
                print("There******************")
                context['message'] = "Your changes has been saved!"    
            except:
                context['error'] = "Something went wrong, please try again later."    

        else :
            try:
                email = request.user.email 
                post_back_url = request.POST.get('post_back_url')  
                password = request.POST.get('password')                 
                faucethub_email=request.POST.get('faucethub_email') 
                try:
                    Provider(                    
                        post_back_user_id=user_id,
                        user=request.user,
                        postback_url=post_back_url,                    
                        payout_method='faucet',
                        bitcoin_address=faucethub_email,  
                        name='',     
                        currency='',
                        provider_payout_percent=0
                    ).save()

                except Exception as e:
                    print('error',e)

                context['message'] = "Your changes has been saved!"    
            except:
                context['error'] = "Something went wrong, please try again later." 
        
        return render(request, self.template_name, context)

class AddWidgetView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/members/addwidget.html'

    def get_context_data(self, id, wid):
        context = super(AddWidgetView, self).get_context_data()
        logger.info('[AddWidgetView] Request - {0}'.format(str('context')))
        if id and wid:
            context['SiteID'] = id
            context['WidgetID'] = wid
        else:
            logger.error('[AddWidgetView] no data')

        return context


class EditWidgetView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/members/addwidget.html'

    def get_context_data(self, id, wid):
        context = super(EditWidgetView, self).get_context_data()
        logger.info('[EditWidgetView] Request - {0}'.format(str('context')))
        if id and wid:
            context['SiteID'] = id
            context['WidgetID'] = wid
        else:
            logger.error('[EditWidgetView] no data')

        return context


def remove_widget_items(request):
    if request.method == 'POST':
        w_id = int(request.POST.get('wid_id'))
        item_id = int(request.POST.get('item_id'))
        if w_id and item_id:
            item = Widget.objects.get(id=item_id)
            item.delete()
            logger.info('[Widget] removed ' + str(item_id))
            return HttpResponseRedirect('widgets/' + str(w_id))
        else:
            logger.error('not w_id and item_id')

    else:
        logger.error('Problem when post data')


@csrf_exempt
def add_widget_data_view(request):
    if request.method == 'POST':
        wid = request.POST.get('wid', None)
        widget, _ = Widget.objects.get_or_create(
            wid=wid
        )
        widget.name = request.POST.get('name', None)
        widget.widgettitle = request.POST.get('widgettitle', None)
        widget.type = request.POST.get('type', None)
        widget.subtype = request.POST.get('subtype', None)
        widget.column = request.POST.get('column', None)
        widget.rows = request.POST.get('rows', None)
        widget.css = request.POST.get('css', None)
        widget.site_id = request.POST.get('sid', None)
        if wid == 'wid':
            widget.wid = hashlib.sha256(str(widget.widgettitle + widget.name + widget.css + random.choice(
                string.ascii_uppercase + string.digits)).encode('utf-8')).hexdigest()
            widget_unqId = widget.wid
        else:
            widget_unqId = wid

        if widget:
            widget.save()
            res = widget_unqId
            logger.info('[addWidgetDataView] {0} Request - {1}'.format(widget, str('widget')))
        else:
            logger.error('[addWidgetDataView] no widget')
    else:
        logger.error('[addWidgetDataView] Wrong request method')

    return JsonResponse(res, safe=False)


class ContactManagerView(LoginRequiredMixin, TemplateView):
    logredirect()
    template_name = 'dashboard/members/contactmanager.html'

    def post(self, request, *args, **kwargs):
        support = Support.objects.create(
            priority=request.POST['priority_id'],
            subject=request.POST['subject'],
            status='Under Review',
            user=request.user,
        )
        support.save()
        if support:
            Message(
                support=support,
                text=request.POST['text'],

            ).save()
        logger.info('[ContactManagerView] Request - {0}'.format(str('site')))
        return HttpResponseRedirect('support')


class MessageView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/members/message.html'

    def get_context_data(self, id):
        context = super(MessageView, self).get_context_data()
        support = Message.objects.filter(support=id).values()
        logger.info('[MessageView] Request - {0}'.format(str('support')))
        if support:
            context['MessageView'] = support
            context['Supportid'] = id
        else:
            logger.error('[MessageView] no data')

        return context

    def post(self, request, *args, **kwargs):
        sid = request.POST['sid']
        Message(
            support_id=sid,
            addedby='User',
            text=request.POST['text'],

        ).save()
        logger.info('[MessageView] Request - {0}'.format(str('message')))
        return HttpResponseRedirect('/dashboard/message/' + sid)


class ProfileView(LoginRequiredMixin, TemplateView):
    logredirect()
    template_name = 'dashboard/members/profile.html'
   


@login_required
def change_password(request):
    template_name = 'dashboard/members/profile.html'
    context = {}
    if request.method == 'POST':
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')
        if password != cpassword:
            context['password'] = "Password and Confirm Password did match"
        else:
            old_password = request.POST.get('old_password')
            usr = SurveyUser.objects.filter(email=request.user.email).first()
            user = authenticate(username=usr.username, password=old_password)
            if not user:
                context['password'] = "Wrong Old password"

            else:
                if user is not None:
                    if user.is_active:
                        u = SurveyUser.objects.get(username=usr.username)
                        u.set_password(password)
                        u.save()
                        context['password'] = "New password updated"

    return render(request, template_name, context)


@csrf_exempt
def getarticle(request):
    if request.method == 'POST':
        res = {}
        wid = request.POST.get('wid', None)
        support = Widget.objects.filter(wid=wid)
        if support:
            res = support
        logger.error('[addWidgetDataView] no widget')
    else:
        logger.error('[addWidgetDataView] Wrong request method')

    posts_serialized = serializers.serialize('json', res)
    return JsonResponse(posts_serialized, safe=False)


class Month(Func):
    function = 'EXTRACT'
    template = '%(function)s(MONTH from %(expressions)s)'
    output_field = models.IntegerField()


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/dashboard')


class BannerView(LoginRequiredMixin, TemplateView):
    logredirect()
    template_name = 'dashboard/members/banner.html'   

   
def BannerView(request):
    print('in function')
    if request.method == 'POST':
        banners = request.POST.getlist('banners')
        count=0
        for banner in banners:            
            bannerSize=request.POST.get(str(count)+'_bannersize')
            partnerName=request.POST.get(str(count)+'_partnername')
            head=request.POST.get(str(count)+'_head')
            body=request.POST.get(str(count)+'_body')
            ratio=request.POST.get(str(count)+'_ratio')
            count=count+1
            bannerSize_Obj=BannerSize.objects.filter(id=bannerSize).first()
            banners = Banners.objects.create(
                        bannersize=bannerSize_Obj,
                        partnername=partnerName,
                        head=head,
                        body=body,
                        ratio=ratio,
                    )
            banners.save()

        return HttpResponseRedirect('/dashboard/members')

    else:
        form = BannerForm()

        return render(request, 'dashboard/members/banner.html', {'form': form,})


