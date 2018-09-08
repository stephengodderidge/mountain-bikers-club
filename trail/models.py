import io
import math
import uuid

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from staticmap import StaticMap, Line

from .gpx import parse, get_coordinates, get_track_image


def user_directory_path(instance, filename):
    return 'trails/{0}/{1}'.format(instance.id, filename)


class Trail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(_('Date published'))

    # Info
    name = models.CharField(_('Title'), max_length=255, null=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    file = models.FileField(_('GPX file'), upload_to=user_directory_path, validators=[FileExtensionValidator(['gpx'])])
    thumbnail = models.FileField(upload_to=user_directory_path, null=True)

    # Track
    location = models.CharField(max_length=255, blank=True, null=True)
    distance = models.FloatField(blank=True, null=True)
    uphill = models.FloatField(blank=True, null=True)
    downhill = models.FloatField(blank=True, null=True)
    min_altitude = models.FloatField(blank=True, null=True)
    max_altitude = models.FloatField(blank=True, null=True)

    # Time
    start_datetime = models.DateTimeField(blank=True, null=True)
    end_datetime = models.DateTimeField(blank=True, null=True)
    total_time = models.FloatField(blank=True, null=True)
    moving_time = models.FloatField(blank=True, null=True)

    # Speed
    average_speed = models.FloatField(blank=True, null=True)
    average_movement_speed = models.FloatField(blank=True, null=True)
    max_speed = models.FloatField(blank=True, null=True)

    class Meta:
        ordering = ['-pub_date', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if bool(self.file):
            with self.file.open() as file:
                gpx_file = file.read()
                name, description, tracks = parse(gpx_file.decode('utf-8'))

                current_track = tracks[0]

                if not self.name:
                    self.name = name or current_track['name'] or _('Unnamed Trail')
                if not self.description:
                    self.description = description or current_track['description'] or None

                current_points = current_track['points']

                self.start_datetime = current_points[0]['time']
                self.end_datetime = current_points[-1]['time']
                self.location = current_track['location']
                self.min_altitude = min(current_track['smoothed_elevations'])
                self.max_altitude = max(current_track['smoothed_elevations'])
                self.uphill = current_track['uphill']
                self.downhill = current_track['downhill']
                self.distance = current_track['distance'] / 1000.
                self.max_speed = max(current_track['smoothed_speeds']) * 3600. / 1000.

                # FIXME moving_time != total_time
                total_time = current_track['total_time']
                self.moving_time = total_time
                self.average_speed = (current_track['distance'] / total_time) * 3600. / 1000.

                self.thumbnail.delete(save=False)
                self.thumbnail.save('thumbnail.jpg', get_track_image(current_points, 360, 180), save=False)

                super().save(*args, **kwargs)
