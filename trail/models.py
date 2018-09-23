import uuid

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


def user_directory_path(instance, filename):
    return 'trails/{0}/{1}'.format(instance.id, filename)


class Trail(models.Model):
    # FIXME Set editable option for other fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(_('Date published'))
    is_draft = models.BooleanField(_('Draft'), default=True)
    is_private = models.BooleanField(_('Private'), default=True, help_text=_('Only you can see this trail'))

    # Info
    name = models.CharField(_('Title'), max_length=255, blank=True)
    description = models.TextField(_('Description'), blank=True)
    tracks = JSONField(null=True)

    # Files
    file = models.FileField(_('GPX file'), upload_to=user_directory_path, validators=[FileExtensionValidator(['gpx'])])
    thumbnail = models.FileField(upload_to=user_directory_path, null=True)
    hero = models.FileField(upload_to=user_directory_path, null=True)

    class Meta:
        ordering = ['-pub_date', 'name']

    def __str__(self):
        return self.name
