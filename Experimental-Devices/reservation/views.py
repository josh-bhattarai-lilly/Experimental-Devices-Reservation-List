from django.shortcuts import render, get_object_or_404, redirect
from .models import Device, VisionPro, ARVRDevice  # Import your Device model
from django.views.generic import TemplateView
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from .forms import AddDeviceForm, DeviceForm


class ReservationView(TemplateView):
    template_name = "reservation/reservation.html"

reservation_view = ReservationView.as_view()


class AdminDashboardView(TemplateView):
    template_name = "reservation/admin_dashboard.html"

dashboard_view = AdminDashboardView.as_view()


class AddDeviceView(TemplateView):
    template_name = "reservation/add_device.html"

    def get(self, request, *args, **kwargs):
        form = AddDeviceForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = AddDeviceForm(request.POST)
        if form.is_valid():
            device_type = form.cleaned_data['device_type']
            serial_number = form.cleaned_data['serial_number']
            description = form.cleaned_data['description']

            # Get the selected device class
            DeviceClass = apps.get_model(app_label='reservation', model_name=device_type)

            # Create a new instance of the selected subclass
            device = DeviceClass.objects.create(serial_number=serial_number, description=description)
            device.save()
            return redirect('list_devices')  # Redirect to the device list view after adding

        return render(request, self.template_name, {'form': form})


add_device_view = AddDeviceView.as_view()


class ListDevicesView(TemplateView):
    template_name = "reservation/list_devices.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all ContentTypes for models that are subclasses of Device
        device_type = ContentType.objects.get_for_model(Device)

        # Find all subclasses of Device
        subclasses = [model for model in apps.get_models() if issubclass(model, Device) and model is not Device]

        # Query all instances of each subclass and combine them
        devices = []
        for subclass in subclasses:
            devices.extend(subclass.objects.all())  # Fetch all instances of this subclass

        context['devices'] = devices  # Add to context
        return context

list_devices_view = ListDevicesView.as_view()


class EditDeviceView(TemplateView):
    template_name = "reservation/edit_device.html"

    def get(self, request, device_id):
        # Attempt to find the device in subclasses
        device = None
        for subclass in (VisionPro, ARVRDevice):  # Add more subclasses here if necessary
            try:
                device = subclass.objects.get(id=device_id)
                break
            except subclass.DoesNotExist:
                continue

        if device is None:
            return redirect('list_devices')  # Or handle the error as appropriate

        form = DeviceForm(instance=device)
        return render(request, self.template_name, {'form': form, 'device': device})

    def post(self, request, device_id):
        device = None
        for subclass in (VisionPro, ARVRDevice):
            try:
                device = subclass.objects.get(id=device_id)
                break
            except subclass.DoesNotExist:
                continue

        if device is None:
            return redirect('list_devices')  # Or handle the error as appropriate

        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            return redirect('list_devices')  # Redirect to the list view after editing

        return render(request, self.template_name, {'form': form, 'device': device})


edit_device_view = EditDeviceView.as_view()


# Delete Device View\

def delete_device_view(request, device_id):
    device = None
    for subclass in (VisionPro, ARVRDevice):  # Add more subclasses if necessary
        try:
            device = subclass.objects.get(id=device_id)
            break
        except subclass.DoesNotExist:
            continue

    if device is None:
        return redirect('list_devices')  # Handle the error, e.g., redirect to the list

    if request.method == 'POST':
        device.delete()
        return redirect('list_devices')  # Redirect to the list view after deletion

    return render(request, 'reservation/delete_device_confirmation.html', {'device': device})

