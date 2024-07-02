from django.urls import path
from accounts import views as AccountViews
from . import views

app_name = "customers"

urlpatterns = [
    path("", AccountViews.customerDashboard, name="custDashboard"),
    path("profile/", views.cprofile, name="cprofile"),
    path("my_orders/", views.my_orders, name="customer_my_orders"),
    path("order_detail/<int:order_number>", views.order_detail, name="order_detail")
]