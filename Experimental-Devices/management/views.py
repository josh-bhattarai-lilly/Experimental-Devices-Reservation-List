from django.shortcuts import render, get_object_or_404, redirect
from .models import Device, VisionPro, ARVRDevice  # Import your Device model
from django.views.generic import TemplateView
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from .forms import AddDeviceForm, DeviceForm
from lilly_auth.models import CustomUser
from django.contrib import messages
from django.views import View
from reservation.models import UserReservationRequest
from reservation.models import UserReservationReturn
from django.contrib.auth.mixins import LoginRequiredMixin


class ManagementView(TemplateView):
    template_name = "management/management.html"

management_view = ManagementView.as_view()


class AdminDashboardView(TemplateView):
    template_name = "management/admin_dashboard.html"

    def get(self, request, *args, **kwargs):
        context={}
        return render(request, self.template_name, context)

dashboard_view = AdminDashboardView.as_view()


class AddDeviceView(TemplateView):
    template_name = "management/add_device.html"

    def get(self, request, *args, **kwargs):
        form = AddDeviceForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = AddDeviceForm(request.POST)
        if form.is_valid():
            device_type = form.cleaned_data['device_type']
            serial_number = form.cleaned_data['serial_number']
            location = form.cleaned_data['location']
            description = form.cleaned_data['description']

            # Get the selected device class
            DeviceClass = apps.get_model(app_label='management', model_name=device_type)

            # Create a new instance of the selected subclass
            device = DeviceClass.objects.create(serial_number=serial_number, description=description, location=location)
            device.save()
            return redirect('list_devices')  # Redirect to the device list view after adding

        return render(request, self.template_name, {'form': form})


add_device_view = AddDeviceView.as_view()


class ListDevicesView(TemplateView):
    template_name = "management/list_devices.html"

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

class FeedbackView(TemplateView):
    template_name = "management/feedback.html"


feedback_view = FeedbackView.as_view()


class EditDeviceView(TemplateView):
    template_name = "management/edit_device.html"

    def get(self, request, device_id):
        # Attempt to find the device in subclasses
        device = None
        for subclass in (VisionPro, ARVRDevice):  # Add more subclasses here if necessary
            try:
                device = subclass.objects.get(serial_number=device_id)
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
                device = subclass.objects.get(serial_number=device_id)
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
            device = subclass.objects.get(serial_number=device_id)
            break
        except subclass.DoesNotExist:
            continue

    if device is None:
        return redirect('list_devices')  # Handle the error, e.g., redirect to the list

    if request.method == 'POST':
        device.delete()
        return redirect('list_devices')  # Redirect to the list view after deletion

    return render(request, 'management/delete_device_confirmation.html', {'device': device})


class ListUsersView(TemplateView):
    template_name = "management/list_users.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = CustomUser.objects.all()
        return context

list_users_view = ListUsersView.as_view()


class DeleteUserView(View):
    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        user.delete()
        messages.success(request, f'User {user.username} has been deleted.')
        return redirect('list_users')


delete_user = DeleteUserView.as_view()


class PromoteToStaffView(View):
    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        user.is_staff = True
        user.save()
        messages.success(request, f'User {user.username} has been promoted to staff.')
        return redirect('list_users')


promote_to_staff = PromoteToStaffView.as_view()


class PromoteToAdminView(View):
    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        user.is_superuser = True
        user.is_staff = True  # Make sure they are staff as well
        user.save()
        messages.success(request, f'User {user.username} has been promoted to admin.')
        return redirect('list_users')


promote_to_admin = PromoteToAdminView.as_view()


class DemoteToUserView(View):
    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        user.is_staff = False
        user.is_superuser = False
        user.save()
        messages.success(request, f'User {user.username} has been demoted to user.')
        return redirect('list_users')


demote_to_user = DemoteToUserView.as_view()


class SendEmaiLView(View):
    def get(self, request):
        user = get_object_or_404(CustomUser, id=request.user.id)
        user.send_user_email('subject', 'test')
        return redirect('admin_dashboard')


send_email_view = SendEmaiLView.as_view()


class UserReservationRequestListView(LoginRequiredMixin, TemplateView):
    template_name = 'management/user_reservation_requests_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch pending and confirmed requests separately
        context['pending_reservation_requests'] = UserReservationRequest.objects.filter(status='Pending').order_by('-created_at')
        context['confirmed_reservation_requests'] = UserReservationRequest.objects.exclude(status='Pending').order_by('-created_at')
        return context

user_reservation_request_list_view = UserReservationRequestListView.as_view()


class UserReservationReturnListView(LoginRequiredMixin, TemplateView):
    template_name = 'management/user_reservation_returns_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch pending and confirmed returns separately
        context['pending_reservation_returns'] = UserReservationReturn.objects.filter(status='Pending').order_by('-created_at')
        context['confirmed_reservation_returns'] = UserReservationReturn.objects.exclude(status='Pending').order_by('-created_at')
        return context

user_reservation_return_list_view = UserReservationReturnListView.as_view()

