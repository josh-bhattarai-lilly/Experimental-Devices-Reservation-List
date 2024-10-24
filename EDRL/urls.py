from django.contrib import admin
from django.urls import path, include  # Include 'include' function

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('lilly_auth.urls')),
    path('', include('management.urls')),  # Correctly include the reservation app's URLs
    path('reserve/', include('reservation.urls')),
]
