from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _

from trail.models import Trail


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    favorite_trails = models.ManyToManyField(Trail, related_name='favorite_by')

    objects = UserManager()

