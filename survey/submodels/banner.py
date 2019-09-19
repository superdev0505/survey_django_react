import logging

from django.contrib.postgres.fields import ArrayField
from django.db.models import *
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_server.db import SHORT_STRING_LENGTH, DEFAULT_STRING_LENGTH, NANO_STRING_LENGTH


logger = logging.getLogger(__name__)


CACHED_MOBILE_BANNERS = {}
CACHED_MOBILE_BANNERS_COUNTERS = {}

CACHED_DESKTOP_BANNERS = {}
CACHED_DESKTOP_BANNERS_COUNTERS = {}

DEVICE_MOBILE = 'MOBILE'
DEVICE_DESKTOP = 'DESKTOP'
DEVICE_TYPES = [
    ('MOBILE', DEVICE_MOBILE),
    ('DESKTOP', DEVICE_DESKTOP),
]


class BannerType(Model):
    name = CharField(max_length=DEFAULT_STRING_LENGTH)
    selector = CharField(max_length=SHORT_STRING_LENGTH)
    size = ArrayField(ArrayField(IntegerField(), size=2), size=4, default=list)

    def __str__(self):
        return '{} - {}'.format(self.name, self.size)


class Banner(Model):
    type = ForeignKey(BannerType, on_delete=CASCADE)
    name = CharField(max_length=DEFAULT_STRING_LENGTH)
    tag_url = CharField(max_length=DEFAULT_STRING_LENGTH)
    tag_id = CharField(max_length=SHORT_STRING_LENGTH)
    device = CharField(max_length=SHORT_STRING_LENGTH, choices=DEVICE_TYPES, default=DEVICE_DESKTOP)
    enabled = BooleanField(default=False)
    rate = IntegerField(default=1)

    def __str__(self):
        return '{} - {} - {}'.format(self.name, self.type, self.device, self.tag_id)

    @classmethod
    def get_banner_set(cls, is_mobile):
        cached_banners = CACHED_MOBILE_BANNERS if is_mobile else CACHED_DESKTOP_BANNERS
        cached_banners_counters = CACHED_MOBILE_BANNERS_COUNTERS if is_mobile else CACHED_DESKTOP_BANNERS_COUNTERS

        if not len(cached_banners):
            cls.refresh_banner_set()

        banners = []
        for key, count in cached_banners_counters.items():
            count = count + 1
            if count > (len(cached_banners.get(key)) - 1):
                count = 0

            cached_banners_counters[key] = count
            banners.append(cached_banners.get(key)[count])

        return banners

    @classmethod
    def refresh_banner_set(cls):

        global CACHED_MOBILE_BANNERS
        global CACHED_DESKTOP_BANNERS
        global CACHED_MOBILE_BANNERS_COUNTERS
        global CACHED_DESKTOP_BANNERS_COUNTERS

        for banner in Banner.objects.exclude(enabled=False):
            selector = banner.type.selector
            size = banner.type.size
            type = str(banner.type)

            existing_banners = CACHED_MOBILE_BANNERS if banner.device == DEVICE_MOBILE else CACHED_DESKTOP_BANNERS

            existing_banners = existing_banners.get(type, [])
            rate = banner.rate
            while rate > 0:
                rate = rate - 1
                existing_banners.append({
                    'selector': selector,
                    'size': size,
                    'url': banner.tag_url,
                    'id': banner.tag_id,
                    'type': banner.type.name,
                    'is_mobile': banner.device == DEVICE_MOBILE
                })
            (CACHED_MOBILE_BANNERS if banner.device == DEVICE_MOBILE else CACHED_DESKTOP_BANNERS)[type] = existing_banners

        banner_counters = {}
        for key in CACHED_MOBILE_BANNERS.keys():
            banner_counters[key] = 0
        CACHED_MOBILE_BANNERS_COUNTERS = banner_counters

        banner_counters = {}
        for key in CACHED_DESKTOP_BANNERS.keys():
            banner_counters[key] = 0
        CACHED_DESKTOP_BANNERS_COUNTERS = banner_counters


@receiver(post_save)
def save_scan(sender, instance, **kwargs):
    if isinstance(instance, Banner):
        Banner.refresh_banner_set()
