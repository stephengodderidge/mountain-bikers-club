import uuid
import gpxpy

from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


# Create your models here.
def user_directory_path(instance, filename):
    return 'trails/{0}/{1}'.format(instance.id, filename)


class Trail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(_('Date published'))

    # Info
    name = models.CharField(_('Title'), max_length=255, null=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    file = models.FileField(_('GPX file'), upload_to=user_directory_path, validators=[FileExtensionValidator(['gpx'])])\
        if settings.DEBUG is True else\
        models.FileField(_('GPX file'), upload_to=user_directory_path, validators=[FileExtensionValidator(['gpx'])], storage=S3Boto3Storage)

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
                gpx = gpxpy.parse(gpx_file.decode('utf-8'))
                track = gpx.tracks[0] if len(gpx.tracks) > 0 else None

                if not self.name:
                    self.name = gpx.name or None

                if not self.description:
                    self.description = gpx.description or None

                if track:
                    if not self.name:
                        self.name = track.name or _('Unnamed Trail')

                    if not self.description:
                        self.description = track.description or None

                    uphill, downhill = track.get_uphill_downhill()
                    moving_time, stopped_time, moving_distance, stopped_distance, max_speed = track.get_moving_data()
                    start_time, end_time = track.get_time_bounds()

                    # Track
                    self.distance = (track.length_3d() or track.length_2d()) / 1000.
                    self.uphill = uphill
                    self.downhill = downhill
                    # self.min_altitude = 0.
                    # self.max_altitude = 0.

                    # Time
                    self.start_datetime = start_time
                    self.end_datetime = end_time
                    # self.total_time = 0
                    self.moving_time = moving_time

                    # Speed
                    self.average_speed = (moving_distance / moving_time) * 3600. / 1000.
                    self.max_speed = max_speed * 3600. / 1000.

                super().save(*args, **kwargs)
