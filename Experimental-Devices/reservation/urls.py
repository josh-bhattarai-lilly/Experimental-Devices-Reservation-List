from django.urls import path
from reservation import views

urlpatterns = [
    path('free-devices/', views.free_devices_view, name='free_devices'),
    path('reserve/device/<str:device_id>/', views.reserve_device_view, name='reserve_device'),
    path('waitlist/', views.waitlist_view, name='waitlist'),
    path('your-devices/', views.your_devices_view, name='your_devices'),
    path('devices/return/<str:device_id>/', views.return_device_view, name='return_device'),
    path('reserve/<int:device_id>/', views.reserve_device_view, name='reserve_device'),
    path('approve_reservation/<int:reservation_id>/', views.approve_reservation_view, name='approve_reservation'),
    path('deny_reservation/<int:reservation_id>/', views.deny_reservation_view, name='deny_reservation'),
    path('return/<int:device_id>/', views.return_device_view, name='return_device'),
    path('approve_return/<int:return_id>/', views.approve_return_view, name='approve_return'),
    path('deny_return/<int:return_id>/', views.deny_return_view, name='deny_return'),
]
