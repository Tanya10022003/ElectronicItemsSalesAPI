from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def activate_user(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        instance.is_active = True
        instance.save()
