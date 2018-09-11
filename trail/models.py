import uuid

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .utils.gpx import parse, get_track_image


def user_directory_path(instance, filename):
    return 'trails/{0}/{1}'.format(instance.id, filename)


class Trail(models.Model):
    # FIXME Editable for other fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(_('Date published'))

    # Info
    name = models.CharField(_('Title'), max_length=255, null=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    tracks = JSONField(null=True)

    # Files
    file = models.FileField(_('GPX file'), upload_to=user_directory_path, validators=[FileExtensionValidator(['gpx'])])
    thumbnail = models.FileField(upload_to=user_directory_path, null=True)

    class Meta:
        ordering = ['-pub_date', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Save the file
        super().save(*args, **kwargs)

        if bool(self.file) and not self.tracks:
            with self.file.open() as file:
                gpx_file = file.read()
                name, description, tracks = parse(gpx_file.decode('utf-8'))

                first_track = tracks[0]

                if not self.name:
                    self.name = name or first_track['name'] or _('Unnamed Trail')
                if not self.description:
                    self.description = description or first_track['description'] or None

                self.tracks = tracks

                # Thumbnail
                self.thumbnail.delete(save=False)
                self.thumbnail.save('thumbnail.jpg', get_track_image(first_track['points'], 360, 180), save=False)

                # Save the data
                super().save(*args, **kwargs)
