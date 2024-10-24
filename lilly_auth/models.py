from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.mail import send_mail
from django.conf import settings

class CustomUser(AbstractUser):
    profile_picture = models.URLField(blank=True, null=True)  # URL of the profile picture
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}' if self.first_name and self.last_name else str(self.email)

    def send_user_email(self, subject, message):
        if self.email:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.email],
                fail_silently=False,
            )

