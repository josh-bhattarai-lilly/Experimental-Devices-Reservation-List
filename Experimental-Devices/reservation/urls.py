from django.contrib import admin
from django.urls import path
from reservation import views as views

urlpatterns = [
    path('', views.reservation_view, name='reservation'),  # Adjust according to your views
]