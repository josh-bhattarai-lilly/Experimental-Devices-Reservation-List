from django.contrib import admin
from django.urls import path, include  # Include 'include' function

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('reservation.urls')),  # Correctly include the reservation app's URLs
]
