import hashlib
import json
import logging
import traceback

from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models import *
from django.utils import timezone

from django_server.db import DEFAULT_STRING_LENGTH

logger = logging.getLogger(__name__)


class UserFingerprint(Model):

    user = ForeignKey('SurveyUser', related_name='fingerprint', on_delete=CASCADE)
    date = DateTimeField(default=timezone.now)
    fingerprint = ForeignKey('Fingerprint', null=False, blank=False, on_delete=CASCADE)

    class Meta:
        indexes = [
            Index(fields=['user']),
            Index(fields=['user', '-date']),
        ]

    @classmethod
    def add(cls, user, data):
        hash = Fingerprint.to_hash(data)
        fingerprint = Fingerprint.objects.filter(hash=hash).first()

        if fingerprint:
            user_fingerprint = UserFingerprint.objects.filter(user=user, fingerprint=fingerprint).first()
            if user_fingerprint:
                return False

        if not fingerprint:
            fingerprint = Fingerprint.create(hash, data)

        UserFingerprint.objects.create(user=user, fingerprint=fingerprint)
        return True


class Fingerprint(Model):

    hash = CharField(max_length=DEFAULT_STRING_LENGTH)
    date = DateTimeField(default=timezone.now)
    data = JSONField(default=dict)

    userAgent = TextField(blank=True, null=True, default='')
    language = TextField(blank=True, null=True, default='')
    colorDepth = IntegerField(default=0)
    deviceMemory = IntegerField(default=0)
    hardwareConcurrency = IntegerField(default=0)
    screenResolution = ArrayField(IntegerField(), size=2, default=list)
    availableScreenResolution = ArrayField(IntegerField(), size=2, default=list)
    timezoneOffset = IntegerField(default=0)
    timezone = TextField(blank=True, null=True, default='')
    sessionStorage = BooleanField(default=False)
    localStorage = BooleanField(default=False)
    indexedDb = BooleanField(default=False)
    addBehavior = BooleanField(default=False)
    openDatabase = BooleanField(default=False)
    cpuClass = TextField(blank=True, null=True, default='')
    platform = TextField(blank=True, null=True, default='')
    plugins = ArrayField(TextField(), default=list)
    webglVendorAndRenderer = TextField(blank=True, null=True, default='')
    adBlock = BooleanField(default=False)
    hasLiedLanguages = BooleanField(default=False)
    hasLiedResolution = BooleanField(default=False)
    hasLiedOs = BooleanField(default=False)
    hasLiedBrowser = BooleanField(default=False)
    touchSupport = BooleanField(default=False)
    fonts = ArrayField(TextField(), default=list)
    audio = TextField(blank=True, null=True, default='')

    class Meta:
        indexes = [
            Index(fields=['hash']),
            Index(fields=['hash', '-date']),
        ]

    @staticmethod
    def create(hash, data):
        fingerprint = Fingerprint(hash=hash)

        try:
            for i in data:
                key = i.get('key')
                value = i.get('value', None)

                if value is None:
                    logger.error('[FINGERPRINT] no value for key {} in {}'.format(key, data))
                    continue
                if not hasattr(fingerprint, key):
                    continue
                if key == 'deviceMemory' and isinstance(value, str):
                    continue
                if key == 'touchSupport':
                    value = value == 1
                if key == 'plugins':
                    value = [i[0] for i in value]

                fingerprint.__setattr__(key, value)

            fingerprint.save()
        except Exception as e:
            logger.error(e)
            logger.error('[FINGERPRINT] ERROR - {}'.format(data))
            traceback.print_exc()

        return fingerprint

    @staticmethod
    def to_hash(data):
        return hashlib.sha256(json.dumps(data).encode('utf-8')).hexdigest()
