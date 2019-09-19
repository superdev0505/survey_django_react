from django.contrib.sitemaps import Sitemap

from survey.submodels.article import Article

class SurveySitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Article.objects.filter(enabled=True)

    def lastmod(self, obj):
        return obj.modified

    def location(self, obj):
        return '/article/' + obj.url


sitemaps = {
    'survey': SurveySitemap,
}