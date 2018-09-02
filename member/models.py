from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from trail.models import Trail


class User(AbstractUser):
    email = models.EmailField(
        _('email address'),
        unique=True,
        blank=False,
        error_messages={
            'unique': _("A user with that email address already exists."),
        },
    )
    favorite_trails = models.ManyToManyField(Trail, related_name='favorite_by')
