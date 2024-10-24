from django.db import models
from django.apps import apps
from django.utils import timezone
from django.utils.timesince import timesince
from django.contrib.auth import get_user_model
CustomUser = get_user_model()  # Dynamically get the custom user model


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  # Updated to use CustomUser
    is_manager = models.BooleanField(default=False)  # Field to indicate if the user is a manager

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Device(models.Model):
    serial_number = models.CharField(max_length=100, unique=True, primary_key=True)  # Serial number of the device
    description = models.TextField(blank=True)  # Short description of the device
    location = models.CharField(max_length=255, blank=True)  # Location of the device
    is_reserved = models.BooleanField(default=False)  # Indicates if the device is reserved
    reserved_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    reserved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # This makes the model abstract, so it won't create a table in the database

    @property
    def id(self):
        """
        Override the id property to return the serial_number.
        """
        return self.serial_number

    @classmethod
    def get_all_subclasses(cls):
        """
        This method returns a list of all subclass models of Device.
        """
        return [model for model in apps.get_models() if issubclass(model, cls) and model is not cls]

    @classmethod
    def get_all_subclass_instances(cls, **filters):
        """
        Returns all instances of all subclasses of Device that match the given filters.
        """
        subclasses = cls.get_all_subclasses()
        instances = []
        for subclass in subclasses:
            instances.extend(subclass.objects.filter(**filters))
        return instances

    @classmethod
    def get_time_elapsed(cls, device):
        """
        Returns the time elapsed since the device was reserved.
        Returns None if the device is not reserved.
        """
        if device.reserved_at:
            return timesince(device.reserved_at, timezone.now())
        return None

    def __str__(self):
        return f"{self.serial_number} - {self.get_device_type()}"

    def get_device_type(self):
        return self.__class__.__name__

    # Update the reservation method to set the time
    def reserve(self, user):
        self.is_reserved = True
        self.reserved_to = user
        self.reserved_at = timezone.now()
        self.save()

    def return_device(self):
        """Mark the device as returned."""
        self.is_reserved = False
        self.reserved_at = None
        self.reserved_to = None
        self.save()  # Save the changes to the database


class VisionPro(Device):
    model_name = models.CharField(max_length=100)  # Additional field specific to VisionPro devices

    def __str__(self):
        return f"VisionPro {self.model_name} - {super().__str__()}"


class ARVRDevice(Device):
    model_type = models.CharField(max_length=100)  # Additional field specific to AR/VR devices

    def __str__(self):
        return f"AR/VR Device {self.model_type} - {super().__str__()}"


class MetaRayBan(Device):
    model_type = models.CharField(max_length=100)  # Additional field specific to AR/VR devices

    def __str__(self):
        return f"AR/VR Device {self.model_type} - {super().__str__()}"
