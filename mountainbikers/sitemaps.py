from django.contrib import sitemaps
from django.urls import reverse
from django.apps import apps as django_apps


class StaticViewSitemap(sitemaps.Sitemap):
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return ['home']

    def location(self, item):
        return reverse(item)


class FlatPageSitemap(sitemaps.Sitemap):
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        Site = django_apps.get_model('sites.Site')
        current_site = Site.objects.get_current()
        return current_site.flatpage_set.filter(registration_required=False)
