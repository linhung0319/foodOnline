import os
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import FoodItem


@receiver(pre_delete, sender=FoodItem)
def pre_delete_vendor_receiver(sender, instance, **kwargs):
    # Delete image
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
