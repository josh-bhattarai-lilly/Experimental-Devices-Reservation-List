from django.db import models
from django.contrib.auth.models import User

class Device(models.Model):
    serial_number = models.CharField(max_length=100, unique=True)  # Serial number of the device
    description = models.TextField(blank=True)  # Short description of the device
    is_reserved = models.BooleanField(default=False)  # Indicates if the device is reserved
    reserved_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # User who reserved the device

    class Meta:
        abstract = True  # This makes the model abstract, so it won't create a table in the database

    def __str__(self):
        return f"{self.serial_number}"

class VisionPro(Device):
    model_name = models.CharField(max_length=100)  # Additional field specific to VisionPro devices

    def __str__(self):
        return f"VisionPro {self.model_name} - {super().__str__()}"

class ARVRDevice(Device):
    model_type = models.CharField(max_length=100)  # Additional field specific to AR/VR devices

    def __str__(self):
        return f"AR/VR Device {self.model_type} - {super().__str__()}"
