from django.urls import path
from . import views


app_name = "accounts"

urlpatterns = [
    path("registerUser/", views.registerUser, name="registerUser"),
    path("registerVendor/", views.registerVendor, name="registerVendor"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("myAccount/", views.myAccount, name="myAccount"),
    path("customerDashboard/", views.customerDashboard, name="customerDashboard"),
    path("vendorDashboard/", views.vendorDashboard, name="vendorDashboard"),
]