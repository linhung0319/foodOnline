from django.urls import path
from . import views


app_name = "accounts"

urlpatterns = [
    path("registerUser/", views.registerUser, name="registerUser"),
    path("registerVendor/", views.registerVendor, name="registerVendor"),
]