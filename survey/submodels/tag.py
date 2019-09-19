from django.db.models import *

from django_server.db import DEFAULT_STRING_LENGTH


class Tag(Model):
    text = CharField(max_length=DEFAULT_STRING_LENGTH)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['text']
        indexes = [
            Index(fields=['text']),
        ]