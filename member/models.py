from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from trail.models import Trail


class User(AbstractUser):
    email = models.EmailField(
        _('email address'),
        unique=True,
        blank=False,
        help_text=_('Required. No bullshit, I promise.'),
        error_messages={
            'unique': _('A user with that email address already exists.'),
        },
    )
    favorite_trails = models.ManyToManyField(Trail, related_name='favorite_by')
    is_premium = models.BooleanField(_('Premium member'), default=False)
    premium_until = models.DateField(_('Premium until'), null=True)
