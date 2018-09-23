from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf.urls.static import static

from member import views as member_views
from .sitemaps import FlatPageSitemap, StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'flatpages': FlatPageSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('robots.txt', include('robots.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    path('shell/', include('shell.urls')),
    path('@<str:username>/', member_views.main, name='member__main'),
    path('dashboard/', include('dashboard.urls')),
    path('trail/', include('trail.urls')),
    path('member/', include('member.urls')),
    path('', include('discover.urls')),
]

# Otherwise served via Amazon S3
if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
