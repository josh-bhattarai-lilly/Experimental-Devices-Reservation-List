from django.contrib import admin
from django.urls import path
from management import views as views

urlpatterns = [
    path('', views.management_view, name='management'),
    path('admin-dashboard', views.dashboard_view, name='admin_dashboard'),
    path('add-device', views.add_device_view, name='add_device'),
    path('list-devices', views.list_devices_view, name='list_devices'),
    path('edit-device/<str:device_id>/', views.edit_device_view, name='edit_device_view'),
    path('delete-device/<str:device_id>/', views.delete_device_view, name='delete_device_view'),
    path('feedback', views.feedback_view, name='feedback_view'),
    path('list-users', views.list_users_view, name='list_users'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('users/promote-staff/<int:user_id>/', views.promote_to_staff, name='promote_to_staff'),
    path('users/promote-admin/<int:user_id>/', views.promote_to_admin, name='promote_to_admin'),
    path('users/demote/<int:user_id>/', views.demote_to_user, name='promote_to_user'),

]