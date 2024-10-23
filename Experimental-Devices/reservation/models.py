from django.db import models
from lilly_auth.models import CustomUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


# Create your models here.

class UserReservationRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    # Use GenericForeignKey for device relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=100)
    device = GenericForeignKey('content_type', 'object_id')

    status = models.CharField(max_length=20,
                              choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Denied', 'Denied')],
                              default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)


class UserReservationReturn(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    # Use GenericForeignKey for device relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=100)
    device = GenericForeignKey('content_type', 'object_id')

    status = models.CharField(max_length=20,
                              choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Denied', 'Denied')],
                              default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
