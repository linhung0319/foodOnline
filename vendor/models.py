from django.db import models
from accounts.models import User, UserProfile


class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="vendor")
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name="vendor")
    vendor_name = models.CharField(max_length=50)
    vendor_license = models.ImageField(upload_to="vendor/license")
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modfied_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name
