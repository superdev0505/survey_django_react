from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportExportModelAdmin

from survey.submodels.article import Article
from survey.submodels.banner import Banner, BannerType
from survey.submodels.blog import BlogPage
from survey.submodels.price import Price, BTCPrice, PriceResource
from survey.submodels.provider import Provider
from survey.submodels.survey import Choice, Question, QuestionAnswer
from survey.submodels.tag import Tag
from survey.models import SurveyUser
from survey.submodels.transaction import UserTransaction, ProviderTransaction
from survey.submodels.vpn import Vpn

admin.site.site_header = "Survey Admin"


@admin.register(SurveyUser)
class SurveyUserAdmin(UserAdmin):
    list_display = ['username', 'ref_id', 'provider', 'provider_user_id', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']
    search_fields = ['username', 'ref_id', 'provider__name', 'provider_user_id', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


@admin.register(Vpn)
class VpnAdmin(admin.ModelAdmin):
    list_display = ['ip']
    search_fields = ['ip']


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'postback_url', 'currency', 'question_count', 'payout_method', 'provider_payout_percent', 'bitcoin_address', 'payout_hide']
    search_fields = ['id', 'name', 'postback_url', 'currency', 'payout_method', 'provider_payout_percent', 'bitcoin_address']


@admin.register(UserTransaction)
class UserTransactionAdmin(admin.ModelAdmin):
    list_display = ['date_created','user','amount','date_sent','payout_status','payout_currency','payout_user_hash']
    search_fields = ['date_created','user__ref_id', 'user__first_name','user__last_name','user__username','user__email','amount','date_sent','payout_status','payout_currency','payout_user_hash']


@admin.register(ProviderTransaction)
class ProviderTransactionAdmin(admin.ModelAdmin):
    list_display = ['date_created','provider','amount','date_sent','payout_status','payout_currency','payout_user_hash']
    search_fields = ['date_created','provider__name','amount','date_sent','payout_status','payout_currency','payout_user_hash']


@admin.register(Price)
class ProviderTransactionAdmin(ImportExportModelAdmin):
    resource_class = PriceResource
    list_display = ['country', 'provider', 'mobile', 'desktop']
    search_fields = ['country', 'provider', 'mobile', 'desktop']


@admin.register(BTCPrice)
class ProviderTransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'amount']
    search_fields = ['date', 'amount']


@admin.register(BlogPage)
class BlogPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'created', 'body']
    search_fields = ['title', 'created', 'body']


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['name', 'enabled', 'type', 'device', 'tag_url', 'tag_id', 'rate']
    search_fields = ['name', 'enabled', 'type', 'device', 'tag_url', 'tag_id', 'rate']
    ordering = ['-enabled', 'device', 'type']


@admin.register(BannerType)
class BannerTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'selector', 'size']
    search_fields = ['name', 'selector', 'size']


admin.site.register(Article, admin.ModelAdmin)
