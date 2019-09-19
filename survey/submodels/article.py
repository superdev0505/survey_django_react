import logging

from django.db.models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from django_server.db import DEFAULT_STRING_LENGTH

logger = logging.getLogger(__name__)


CACHED_ARTICLES_LIST = []
CACHED_ARTICLES_KEYS = []


class Article(Model):
    url = CharField(default='', max_length=DEFAULT_STRING_LENGTH)
    title = TextField(default='')
    text = TextField(default='')
    modified = DateTimeField(default=timezone.now)
    enabled = BooleanField(default=True)

    def __str__(self):
        return self.title

    @classmethod
    def get_article(cls, id=0):
        articles = cls.get_articles_set()
        articles_len = len(articles)
        if articles_len > 0:
            return articles[id] if id < articles_len else cls.get_article(id - articles_len)

    @classmethod
    def get_next_article(cls, current_index=0, current_article=None):
        if not current_index and current_article:
            current_index = CACHED_ARTICLES_KEYS.index(current_article.url)
        return cls.get_article(id=current_index + 1)

    @classmethod
    def get_articles_set(cls):
        if not len(CACHED_ARTICLES_LIST):
            cls.refresh_article_set()
        return CACHED_ARTICLES_LIST

    @classmethod
    def refresh_article_set(cls):
        global CACHED_ARTICLES_LIST
        CACHED_ARTICLES_LIST = Article.objects.filter(enabled=True).order_by('-id')
        global CACHED_ARTICLES_KEYS
        CACHED_ARTICLES_KEYS = [article.url for article in CACHED_ARTICLES_LIST]


@receiver(post_save)
def save_article(sender, instance, **kwargs):
    if isinstance(instance, Article):
        Article.refresh_article_set()
        if not instance.url:
            instance.url = str.lower(instance.title.replace(' ', '-'))
            instance.save()
