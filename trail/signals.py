from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Trail


# https://stackoverflow.com/questions/16041232/django-delete-filefield
@receiver(pre_delete, sender=Trail)
def trail_delete_handler(sender, **kwargs):
    instance = kwargs['instance']
    instance.file.delete()
    instance.thumbnail.delete()
    instance.hero.delete()
