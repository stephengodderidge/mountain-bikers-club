from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.apps import apps as django_apps
from django.utils import timezone

from trail.models import Trail
from member.models import User


class TrailSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        return Trail.objects.filter(pub_date__lte=timezone.now(), is_draft=False, is_private=False)

    def location(self, obj):
        return reverse('trail__main', args=[obj.id])


class MemberSitemap(Sitemap):
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return User.objects.filter(is_active=True)

    def location(self, obj):
        return reverse('member__main', args=[obj.username])


class StaticViewSitemap(Sitemap):
    changefreq = 'monthly'
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
