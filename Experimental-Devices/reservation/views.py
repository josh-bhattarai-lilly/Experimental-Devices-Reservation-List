from django.shortcuts import render

# Create your views here.

from django.views.generic import TemplateView


class ReservationView(TemplateView):
    template_name = "reservation/reservation.html"


reservation_view = ReservationView.as_view()

