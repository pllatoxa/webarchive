from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    # на случай, если профиль уже есть
    if hasattr(instance, "profile"):
        instance.profile.save()


# При старте приложения гарантируем, что у всех существующих пользователей есть профили.
# Это нужно, чтобы лента брала ник из профиля даже у старых постов.
def _ensure_profiles():
    for user in User.objects.all():
        Profile.objects.get_or_create(user=user)


_ensure_profiles()
