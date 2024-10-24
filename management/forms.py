from django import forms
from django.apps import apps
from django.contrib.auth import get_user_model  # Import get_user_model to avoid loading issues
from .models import Device
CustomUser = get_user_model()  # Get the custom user model here

class AddDeviceForm(forms.Form):
    device_type = forms.ChoiceField(choices=[], label="Device Type")
    location = forms.CharField(max_length=200, label="Device Location", required=False)
    serial_number = forms.CharField(max_length=100, label="Serial Number")
    description = forms.CharField(widget=forms.Textarea, label="Description", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically get all subclasses of Device and populate the choices
        subclasses = [model for model in apps.get_models() if issubclass(model, Device) and model is not Device]
        self.fields['device_type'].choices = [(subclass.__name__, subclass.__name__) for subclass in subclasses]

    def clean(self):
        cleaned_data = super().clean()
        is_reserved = cleaned_data.get('is_reserved')
        reserved_to = cleaned_data.get('reserved_to')

        # Logic to set fields to None if conditions are met
        if is_reserved is None:
            cleaned_data['reserved_at'] = None
            cleaned_data['reserved_to'] = None
        if reserved_to is None:
            cleaned_data['reserved_at'] = None
            cleaned_data['is_reserved'] = False

        return cleaned_data


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['serial_number', 'description', 'location', 'is_reserved', 'reserved_to']  # Include fields you want to edit

    def clean(self):
        cleaned_data = super().clean()

        is_reserved = cleaned_data.get('is_reserved')
        reserved_to = cleaned_data.get('reserved_to')

        # If is_reserved is False, set reserved_to and reserved_at to None
        if is_reserved is False:
            cleaned_data['reserved_to'] = None
            cleaned_data['reserved_at'] = None

        # If reserved_to is None, set reserved_at and is_reserved to None
        if reserved_to is None:
            cleaned_data['reserved_at'] = None
            cleaned_data['is_reserved'] = False  # Set to False if reserved_to is None

        return cleaned_data
