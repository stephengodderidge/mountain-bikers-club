from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Trail


# Register your models here.
class TrailAdmin(admin.ModelAdmin):
    list_display = ('name', 'pub_date', 'author')
    search_fields = ['name']
    actions = ['update_from_gpx']

    def update_from_gpx(self, request, queryset):
        for obj in queryset:
            obj.save()
    update_from_gpx.short_description = _('Update from GPX')


admin.site.register(Trail, TrailAdmin)
