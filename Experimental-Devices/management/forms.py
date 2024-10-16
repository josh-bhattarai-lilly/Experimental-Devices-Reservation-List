from django import forms
from django.apps import apps
from .models import Device

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

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['serial_number', 'description', 'location', 'is_reserved', 'reserved_to']  # Include fields you want to edit
