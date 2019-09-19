from django.core.cache import cache
from django.db.models import *
from django.utils import timezone


class Vpn(Model):
    ip = TextField(default='', blank=False, null=False, verbose_name='ip')
    is_vpn = BooleanField(default=False)
    created = DateTimeField(auto_now_add=True)

    @staticmethod
    def get_by_ip(ip):
        # return get_from_cache('vpn-{}'.format(ip), lambda: Vpn.objects.filter(ip=ip).first(), timeout=3600)
        return Vpn.objects.filter(ip=ip).first()

    @staticmethod
    def set_by_ip(ip, is_vpn):
        vpn,_ = Vpn.objects.get_or_create(ip=ip)
        vpn.created = timezone.now()
        vpn.is_vpn = is_vpn
        vpn.save()

        key = 'vpn-{}'.format(ip)
        cache.set(key, vpn, 3600)
        return vpn

    class Meta:
        indexes = [
            Index(fields=['ip']),
        ]

    def __str__(self):
        return '{} - {} - {}'.format(self.ip, self.is_vpn, self.created)
