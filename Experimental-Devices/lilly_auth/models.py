from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Add any extra fields you want to store
    profile_picture = models.URLField(blank=True, null=True)  # URL of the profile picture
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username
