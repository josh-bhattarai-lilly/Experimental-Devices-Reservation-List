from django.shortcuts import  get_object_or_404, redirect
from management.models import Device, VisionPro, ARVRDevice
from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from .models import UserReservationRequest, UserReservationReturn
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.http import JsonResponse

# Use CustomUser instead of default User
CustomUser = get_user_model()

class FreeDevicesView(TemplateView):
    template_name = "reservation/free_devices.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Query all instances of subclasses of Device where is_reserved is False or is null
        free_devices = Device.get_all_subclass_instances(is_reserved=False) + Device.get_all_subclass_instances(is_reserved__isnull=True)

        context['free_devices'] = free_devices  # Add to context
        return context

    def post(self, request, *args, **kwargs):
        # Get the device serial number from the POST request
        device_id = request.POST.get('device_id')

        if device_id:
            # Redirect the POST request to the ReserveDeviceView
            return redirect('reserve_device', device_id=device_id)
        else:
            # If no device_id is provided, reload the same page
            return self.get(request, *args, **kwargs)

# Call the as_view() method here
free_devices_view = FreeDevicesView.as_view()


class ReserveDeviceView(LoginRequiredMixin, View):
    def post(self, request, device_id):
        # Iterate over all subclasses to find the device with the given serial number
        device = None
        for subclass in Device.get_all_subclasses():
            try:
                device = subclass.objects.get(serial_number=device_id)
                break  # Stop the loop if device is found
            except subclass.DoesNotExist:
                continue  # Try the next subclass if not found

        if not device:
            # If no device is found, return a 404 error
            return get_object_or_404(Device, serial_number=device_id)

        # Get the ContentType for the device model
        device_content_type = ContentType.objects.get_for_model(device)

        # Extract department, role, and reason from the POST request
        department = request.POST.get('department')
        role = request.POST.get('role')
        reason = request.POST.get('reason')

        # Create a UserReservationRequest instead of reserving immediately
        reservation_request = UserReservationRequest.objects.create(
            user=request.user,
            content_type=device_content_type,
            object_id=device.id,
            department=department,
            role=role,
            reason=reason,
            status='Pending'
        )

        # Send an email to admins with allow/deny links
        admin_users = CustomUser.objects.filter(is_staff=True)
        allow_url = request.build_absolute_uri(reverse('approve_reservation', args=[reservation_request.id]))
        deny_url = request.build_absolute_uri(reverse('deny_reservation', args=[reservation_request.id]))

        email_body = f"""
        A new reservation request has been made by {request.user.username} for device {device.serial_number}.
        Department: {department}
        Role: {role}
        Reason: {reason}

        Please review the request:

        Approve: {allow_url}
        Deny: {deny_url}
        """

        subject = 'New Device Reservation Request'

        # Use the send_user_email function to send an email to each admin
        for admin in admin_users:
            admin.send_user_email(subject, email_body)

        # Return a JSON response with the device serial number
        return JsonResponse({'device_serial_number': device.serial_number}, status=200)

# Call the as_view() method here
reserve_device_view = ReserveDeviceView.as_view()


class YourDevicesView(LoginRequiredMixin, ListView):
    template_name = 'reservation/your_devices.html'
    context_object_name = 'devices'

    def get_queryset(self):
        # Get all devices reserved by the current user, excluding devices with pending return requests
        devices = Device.get_all_subclass_instances(reserved_to=self.request.user)

        # Exclude devices that have a pending return request
        pending_returns = UserReservationReturn.objects.filter(user=self.request.user, status='Pending').values_list('object_id', flat=True)
        devices = [device for device in devices if str(device.serial_number) not in pending_returns]

        for device in devices:
            # Calculate time elapsed since reservation using the class method
            device.time_elapsed = Device.get_time_elapsed(device)

        return devices

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add return requests to the context
        return_requests = UserReservationReturn.objects.filter(user=self.request.user, status='Pending')
        context['return_requests'] = return_requests

        # Add reservation requests to the context
        reservation_requests = UserReservationRequest.objects.filter(user=self.request.user, status='Pending')
        context['reservation_requests'] = reservation_requests

        return context

your_devices_view = YourDevicesView.as_view()


class ApproveReservationView(LoginRequiredMixin, View):
    def get(self, request, reservation_id):
        reservation = get_object_or_404(UserReservationRequest, id=reservation_id)
        if request.user.is_staff:
            reservation.status = 'Approved'
            reservation.device.reserve(reservation.user)  # Reserve the device for the user
            reservation.device.save()
            reservation.save()
        return redirect('list_requests')

approve_reservation_view = ApproveReservationView.as_view()


class DenyReservationView(LoginRequiredMixin, View):
    def get(self, request, reservation_id):
        reservation = get_object_or_404(UserReservationRequest, id=reservation_id)
        if request.user.is_staff:
            reservation.status = 'Denied'
            reservation.save()
        return redirect('list_requests')

deny_reservation_view = DenyReservationView.as_view()


class ReturnDeviceView(LoginRequiredMixin, View):
    def post(self, request, device_id):
        # Iterate over all subclasses to find the device with the given serial number
        device = None
        for subclass in Device.get_all_subclasses():
            try:
                device = subclass.objects.get(serial_number=device_id)
                break  # Stop the loop if the device is found
            except subclass.DoesNotExist:
                continue  # Try the next subclass if not found

        if not device:
            # If no device is found, return a 404 error
            return get_object_or_404(Device.get_all_subclasses(), serial_number=device_id)

        # Create a UserReservationReturn request
        return_request = UserReservationReturn.objects.create(
            user=request.user,
            content_type=ContentType.objects.get_for_model(device),
            object_id=device.serial_number,  # Use serial_number instead of device.id
            status='Pending'
        )

        # Notify admins about the return request
        admin_emails = CustomUser.objects.filter(is_staff=True).values_list('email', flat=True)
        allow_url = request.build_absolute_uri(reverse('approve_return', args=[return_request.id]))
        deny_url = request.build_absolute_uri(reverse('deny_return', args=[return_request.id]))

        email_body = f"""
        A return request has been made by {request.user.username} for device {device.serial_number}.
        Please review the request:

        Approve: {allow_url}
        Deny: {deny_url}
        """

        # Send email to admins using CustomUser's send_user_email method
        for email in admin_emails:
            admin = CustomUser.objects.get(email=email)
            admin.send_user_email('Device Return Request', email_body)

        return redirect('your_devices')

return_device_view = ReturnDeviceView.as_view()


class ApproveReturnView(LoginRequiredMixin, View):
    def get(self, request, return_id):
        return_request = get_object_or_404(UserReservationReturn, id=return_id)
        if request.user.is_staff:
            return_request.status = 'Confirmed'
            return_request.device.return_device()
            return_request.device.save()
            return_request.save()
        return redirect('list_returns')

approve_return_view = ApproveReturnView.as_view()


class DenyReturnView(LoginRequiredMixin, View):
    def get(self, request, return_id):
        return_request = get_object_or_404(UserReservationReturn, id=return_id)
        if request.user.is_staff:
            return_request.status = 'Denied'
            return_request.save()
        return redirect('list_returns')

deny_return_view = DenyReturnView.as_view()


class WaitlistView(TemplateView):
    template_name = "reservation/waitlist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

waitlist_view = WaitlistView.as_view()

class CancelReturnRequestView(LoginRequiredMixin, View):
    def post(self, request, request_id):
        return_request = get_object_or_404(UserReservationReturn, id=request_id, user=request.user)
        return_request.delete()  # Delete the return request

        return redirect('your_devices')  # Redirect to the devices view

cancel_return_request_view = CancelReturnRequestView.as_view()


class CancelReservationRequestView(LoginRequiredMixin, View):
    def post(self, request, request_id):
        # Get the reservation request
        reservation_request = get_object_or_404(UserReservationRequest, id=request_id, user=request.user)

        # Cancel the reservation request (you may want to update the status or delete it)
        reservation_request.status = 'Cancelled'  # or reservation_request.delete()
        reservation_request.save()

        return redirect('your_devices')  # Redirect back to your devices page
cancel_reservation_request_view = CancelReservationRequestView.as_view()