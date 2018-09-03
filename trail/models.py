import math
import uuid

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

import trail.gpx as gpx


def user_directory_path(instance, filename):
    return 'trails/{0}/{1}'.format(instance.id, filename)


class Trail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(_('Date published'))

    # Info
    name = models.CharField(_('Title'), max_length=255, null=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    location = models.CharField(_('Location'), max_length=255, blank=True, null=True)
    file = models.FileField(_('GPX file'), upload_to=user_directory_path, validators=[FileExtensionValidator(['gpx'])])

    # Track
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
                parser = gpx.parse(gpx_file.decode('utf-8'))

                name, description, start_time, end_time, location = parser.get_metadata()
                if not self.name:
                    self.name = name or _('Unnamed Trail')
                if not self.description:
                    self.description = description
                self.start_datetime = start_time
                self.end_datetime = end_time
                self.location = location

                min_elevation, max_elevation, uphill, downhill = parser.get_elevation_data()
                self.min_altitude = min_elevation
                self.max_altitude = max_elevation
                self.uphill = uphill
                self.downhill = downhill

                distance, time, max_speed = parser.get_moving_data()
                self.distance = distance / 1000
                self.max_speed = max_speed * 3600. / 1000.

                # FIXME moving_time != total_time
                total_time = math.fabs((end_time - start_time).total_seconds())
                self.moving_time = total_time
                self.average_speed = (distance / total_time) * 3600. / 1000.

                super().save(*args, **kwargs)
