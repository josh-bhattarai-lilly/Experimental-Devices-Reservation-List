from django.shortcuts import render, get_object_or_404, redirect
from management.models import Device, VisionPro, ARVRDevice
from django.views.generic import ListView, TemplateView, View
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib.auth.decorators import login_required
#from .forms import *

class FreeDevicesView(TemplateView):
    template_name = "reservation/free_devices.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        # Query all instances of subclasses of Device where is_reserved is False or is null
        free_devices = Device.get_all_subclass_instances(is_reserved=False) + Device.get_all_subclass_instances(is_reserved__isnull=True)

        context['free_devices'] = free_devices  # Add to context
        return context

free_devices_view = FreeDevicesView.as_view()


def reserve_device(request, device_id):
    if request.method == 'POST':
        device = get_object_or_404(Device, serial_number=device_id)
        device.reserve(request.user)  # Use the reserve method from the Device model
        return redirect('free_devices')  # Redirect back to the free devices page


class WaitlistView(TemplateView):
    template_name = "reservation/waitlist.html"

waitlist_view = WaitlistView.as_view()


class ReserveDeviceView(LoginRequiredMixin, View):

    def get(self, request, device_id):
        # Query all device subclasses and filter for unreserved devices
        devices = Device.get_all_subclass_instances(is_reserved=False)

        # Find the device with the matching ID
        device = next((d for d in devices if d.serial_number == device_id), None)

        if device:
            return render(request, 'management/reserve_device.html', {'device': device})
        else:
            return redirect('error_page')  # Handle case where no device is found

    def post(self, request, device_id):
        # Query all device subclasses and filter for unreserved devices
        devices = Device.get_all_subclass_instances(is_reserved=False)

        # Find the device with the matching ID
        device = next((d for d in devices if d.serial_number == device_id), None)

        if device:
            # Use the reserve method to set the device as reserved by the current user
            device.reserve(request.user)  # Call the reserve method

            # Redirect to the free devices page or another success page
            return redirect('free_devices')
        else:
            return redirect('error_page')  # Handle case where no device is found

reserve_device_view = ReserveDeviceView.as_view()

from django.contrib.auth import get_user_model
class YourDevicesView(LoginRequiredMixin, ListView):
    template_name = 'reservation/your_devices.html'
    context_object_name = 'devices'

    def get_queryset(self):
        # Get all device subclasses reserved by the current user
        devices = Device.get_all_subclass_instances(reserved_to=self.request.user)

        for device in devices:
            # Calculate time elapsed since reservation using the class method
            device.time_elapsed = Device.get_time_elapsed(device)
        return devices

your_devices_view = YourDevicesView.as_view()


@login_required
def return_device_view(request, device_id):
    # Retrieve the specific subclass of Device the user has reserved
    subclasses = Device.get_all_subclasses()
    device = None

    # Loop through subclasses to find the device
    for subclass in subclasses:
        try:
            device = subclass.objects.get(serial_number=device_id, reserved_to=request.user)
            break  # Exit loop if found
        except subclass.DoesNotExist:
            continue  # Try next subclass if not found

    # If device is not found, redirect or handle the error
    if device is None:
        return redirect('your_devices')  # Or handle error more gracefully

    # Call the return_device method to update the device status
    device.return_device()

    return redirect('your_devices')  # Redirect to the devices page



