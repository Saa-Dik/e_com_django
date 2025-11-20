from django.urls import path
from . import views
from.admin_dashboard import order_dashboard

app_name = "core"
urlpatterns = [
    path('', views.home, name='home'),
    path("admin/order-dashboard/", order_dashboard, name="order_dashboard"),
]