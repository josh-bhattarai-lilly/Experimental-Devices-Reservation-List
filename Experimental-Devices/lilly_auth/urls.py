from django.urls import path
from . import views as views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('callback/', views.auth_callback, name='auth_callback'),
    path('profile-picture/', views.profile_picture_view, name='profile_picture'),
]
