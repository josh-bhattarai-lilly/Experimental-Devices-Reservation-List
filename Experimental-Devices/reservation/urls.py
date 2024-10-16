from django.contrib import admin
from django.urls import path
from reservation import views as views

urlpatterns = [
    path('free-devices', views.free_devices_view, name='free_devices'),
    path('reserve/device/<int:device_id>/', views.reserve_device, name='reserve_device'),
    path('waitlist', views.waitlist_view, name='waitlist'),
]