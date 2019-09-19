import logging
import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from django.core.cache import cache
from django.db.models import *
from django.utils import timezone
from django_countries.fields import CountryField

from django_server.db import NANO_STRING_LENGTH, LONG_STRING_LENGTH, IPV6_STRING_LENGTH
from survey.submodels.provider import Provider, PAYOUT_USER_BITCOIN, PAYOUT_PROVIDER_BITCOIN
from survey.subviews.payout import faucethub

USER_CAN_CHANGE_PROFILE_IN_DAY = 2
USER_FIELDS_TO_CHANGE = ['bitcoin_address', 'provider_user_id', 'ref_id']

logger = logging.getLogger(__name__)


class SurveyUser(AbstractUser):

    provider = ForeignKey(Provider, on_delete=CASCADE)
    provider_user_id = TextField(blank=True, null=False, default='')
    ref_id = CharField(max_length=NANO_STRING_LENGTH, default='')
    bitcoin_address = CharField(max_length=LONG_STRING_LENGTH, default='')
    tags = JSONField(default=dict)
    country = CountryField(blank=True, null=True)
    is_suspended = BooleanField(default=False)

    class Meta:
        app_label = 'survey'
        ordering = ['provider']
        indexes = [
            Index(fields=['provider']),
        ]

    def __str__(self):
        return self.ref_id

    @property
    def current_survey(self):
        return self.survey_set.order_by('-created').first()

    def add_tags(self, tags):
        if not len(tags):
            pass
        for tag in tags:
            self.tags[tag] = self.tags.get(tag, 1)
        self.save()

    def can_update_data(self):
        return UserHistory.objects.filter(user=self, date__gte=timezone.now() - timedelta(hours=24)).count() < USER_CAN_CHANGE_PROFILE_IN_DAY

    def set_ref_id(self, ref_id):
        ref = RefIdHistory.objects.filter(id=ref_id).first()

        if not ref:
            raise Exception('Wrong RefId')

        if ref.user != self:
            if ref.user and ref.user.social_auth.count() > 0:
                raise Exception('RefId is already in use!')
            if not ref.bitcoin_address and ref.provider.payout_method in [PAYOUT_USER_BITCOIN]:
                raise Exception('Invalid RefId')
            if RefIdHistory.objects.filter(user=self, provider=ref.provider).exclude(id=ref_id).first():
                raise Exception('Provider {} is already associated with your account!'.format(ref.provider.name))
            else:
                ref.user = self
                ref.save()

        self.ref_id = ref_id
        self.provider = ref.provider
        self.provider_user_id = ref.provider_user_id
        self.bitcoin_address = ref.bitcoin_address
        self.save()

    # Wrapper allows to make batch update with saving information about changes
    def update_data(self, data):
        changes = {}
        for field in USER_FIELDS_TO_CHANGE:
            value = data.get(field)
            if not value or self.__getattribute__(field) == value:
                continue

            if field == 'bitcoin_address' and self.provider.is_user_accepting_bitcoin:
                faucethub.check_address(value)
            elif field == 'ref_id':
                self.set_ref_id(value)

            changes[field] = value
            self.__setattr__(field, value)

        # If user was not changed
        if not len(changes.keys()):
            return False

        self.save()
        UserHistory.objects.create(user=self, changes=changes)
        return True

    @property
    def is_registered(self):
        return self.is_authenticated and hasattr(self, 'provider')


class RefIdHistory(Model):
    id = CharField(primary_key=True, max_length=NANO_STRING_LENGTH)
    user = ForeignKey(SurveyUser, related_name='ref_id_history', on_delete=CASCADE, null=True)
    provider = ForeignKey(Provider, on_delete=CASCADE)
    provider_user_id = TextField(blank=True, null=False, default='')
    bitcoin_address = CharField(max_length=LONG_STRING_LENGTH, default='')

    class Meta:
        indexes = [
            Index(fields=['user']),
            Index(fields=['id']),
        ]

    @classmethod
    def get_or_create_reference(cls, provider, provider_user_id):
        ref = cls.objects.filter(provider=provider, provider_user_id=provider_user_id).first()
        if not ref:
            ref = RefIdHistory.generate_reference(provider, provider_user_id)
        return ref

    @classmethod
    def generate_reference(cls, provider, provider_user_id):
        ref_id = str(uuid.uuid4())[:8]
        if cls.objects.filter(id=ref_id).count():
            return cls.generate_reference(provider, provider_user_id)
        return RefIdHistory.objects.create(id=ref_id, provider=provider, provider_user_id=provider_user_id)


class IPHistory(Model):
    user = ForeignKey(SurveyUser, related_name='ip_history', on_delete=CASCADE)
    ip = CharField(max_length=IPV6_STRING_LENGTH, default='')
    date = DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            Index(fields=['user']),
            Index(fields=['ip']),
            Index(fields=['ip', '-date']),
        ]

    @staticmethod
    def get_blacklist():
        key = 'IP_BLACKLIST'

        ip = cache.get(key)
        if not ip:
            ip = list(IPHistory.objects.filter(user__is_active=False, date__gte=timezone.now() - timedelta(hours=48)).values_list('ip', flat=True))
            cache.set(key, ip, timeout=15)
        return ip


class UserHistory(Model):
    user = ForeignKey(SurveyUser, related_name='user_history', on_delete=CASCADE)
    date = DateTimeField(auto_now_add=True)
    changes = JSONField(default=dict)

    class Meta:
        indexes = [
            Index(fields=['user']),
            Index(fields=['user', '-date']),
        ]


class UserBanHistory(Model):
    user = ForeignKey(SurveyUser, related_name='user_ban_history', on_delete=CASCADE)
    date = DateTimeField(auto_now_add=True)
    timeout = IntegerField(default=0)
    suspend_till = DateTimeField(null=True, blank=True, default=None)
    reason = TextField(default='')

    @classmethod
    def block_user(cls, user, timeout_minutes, reason):
        if UserBanHistory.is_blocked(user):
            logger.info('[Already blocked] TODO check why it appeared {}'.format(user))
            return
        UserBanHistory.objects.create(
            user=user,
            date=timezone.now(),
            timeout=timeout_minutes,
            suspend_till=timezone.now() + timedelta(minutes=timeout_minutes),
            reason=reason
        )
        user.is_suspended = True
        user.save()

    @classmethod
    def unblock_user(cls, user):
        is_blocked = UserBanHistory.is_blocked(user)
        if not is_blocked:
            user.is_suspended = False
            user.save()

        return not is_blocked

    @staticmethod
    def is_blocked(user):
        return UserBanHistory.objects.filter(user=user, suspend_till__gt=timezone.now()).order_by('-suspend_till').first()


class UserFlags(Model):
    VPN = 'VPN'
    ADBLOCK = 'ADBLOCK'
    BOT = 'BOT'
    ZOMBIE = 'ZOMBIE'
    OFTNIP = 'OFTNIP'
    OFTNSOLV = 'OFTNSOLV'
    CONTRADC = 'CONTRADC'
    SAMEIP = 'SAMEIP'
    SAMEFGPT = 'SAMEFGPT'
    NO_FGPT = 'NO_FGPT'
    NO_MOUSE = 'NO_MOUSE'
    MOUSE_PH = 'MOUSE_PH'

    user = ForeignKey(SurveyUser, related_name='user_flags', on_delete=CASCADE)
    date = DateTimeField(auto_now_add=True)
    key = CharField(max_length=NANO_STRING_LENGTH)

    class Meta:
        indexes = [
            Index(fields=['user']),
            Index(fields=['user', '-date']),
        ]


class UserFeedback(Model):
    NO_VPN = 'NOVPN'
    NO_ADBLOCK = 'NOADBLOCK'
    NO_BOT = 'NOBOT'

    user = ForeignKey(SurveyUser, related_name='user_feedback', on_delete=CASCADE)
    date = DateTimeField(auto_now_add=True)
    type = CharField(max_length=NANO_STRING_LENGTH)
    text = TextField()
    fingerprint = TextField()

    class Meta:
        indexes = [
            Index(fields=['user']),
            Index(fields=['user', '-date']),
        ]