from django.db.models import *


class BlogPage(Model):
    title = TextField(default='', blank=False, null=False)
    body = TextField(default='', blank=False, null=False)
    created = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Blog - Pages'

    def __str__(self):
        return '{} - {}'.format(self.created, self.title)

    @property
    def body_short(self):
        return self.body[:255] + '...'
