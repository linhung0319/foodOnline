import os
from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from .models import User, UserProfile

@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            # Create the userprofile if not exist
            UserProfile.objects.create(user=instance)

# @receiver(pre_save, sender=User)
# def pre_save_profile_receiver(sender, instance, **kwargs):
#     print(instance.username, "This user is being saved")


@receiver(pre_delete, sender=UserProfile)
def pre_delete_profile_receiver(sender, instance, **kwargs):
    # Delete profile_picture
    if instance.profile_picture:
        if os.path.isfile(instance.profile_picture.path):
            os.remove(instance.profile_picture.path)

    # Delete cover_photo
    if instance.cover_photo:
        if os.path.isfile(instance.cover_photo.path):
            os.remove(instance.cover_photo.path)
