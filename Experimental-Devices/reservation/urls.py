from django.contrib import admin
from django.urls import path
from reservation import views as views

urlpatterns = [
    path('', views.reservation_view, name='reservation'),
    path('admin-dashboard', views.dashboard_view, name='admin_dashboard'),
    path('add-device', views.add_device_view, name='add_device'),
    path('list-devices', views.list_devices_view, name='list_devices'),
    path('edit-device/<int:device_id>/', views.edit_device_view, name='edit_device_view'),
    path('delete-device/<int:device_id>/', views.delete_device_view, name='delete_device_view'),
]