import os
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Vendor


@receiver(pre_delete, sender=Vendor)
def pre_delete_vendor_receiver(sender, instance, **kwargs):
    # Delete vendor_license
    if instance.vendor_license:
        if os.path.isfile(instance.vendor_license.path):
            os.remove(instance.vendor_license.path)
