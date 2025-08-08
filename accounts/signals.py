import os
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

# Ensure a Profile exists for each new User (safe get_or_create)
@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

# When a Profile's picture is changed, delete the old file from disk/storage
@receiver(pre_save, sender=Profile)
def delete_old_profile_picture_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Profile.objects.get(pk=instance.pk)
    except Profile.DoesNotExist:
        return
    old_file = old.profile_picture
    new_file = instance.profile_picture
    if old_file and old_file != new_file:
        # safe remove only if file exists on filesystem
        if hasattr(old_file, 'path') and os.path.isfile(old_file.path):
            old_file.delete(save=False)

# When a Profile is deleted, delete its picture file
@receiver(post_delete, sender=Profile)
def delete_profile_picture_on_delete(sender, instance, **kwargs):
    file = instance.profile_picture
    if file:
        file.delete(save=False)
