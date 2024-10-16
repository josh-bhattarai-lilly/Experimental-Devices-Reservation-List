from django.contrib import admin
from django.urls import path
from reservation import views as views

urlpatterns = [
    path('free-devices', views.free_devices_view, name='free_devices'),
    path('reserve/device/<str:device_id>/', views.reserve_device_view, name='reserve_device'),
    path('waitlist', views.waitlist_view, name='waitlist'),
    path('your-devices/', views.your_devices_view, name='your_devices'),
    path('devices/return/<str:device_id>/', views.return_device_view, name='return_device'),
]