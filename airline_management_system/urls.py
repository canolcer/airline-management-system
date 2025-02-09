from django.contrib import admin
from django.urls import path

from airline import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),

    # Airplane urls
    path('airplanes/', views.airplanes),
    path('airplanes/<int:id>/', views.airplane_detail),
    path('airplanes/<int:id>/flights/', views.get_flights_from_airplane),

    # Flight urls
    path('flights/', views.flights),
    path('flights/<int:id>/', views.flight_detail),
    path('flights/<int:id>/reservations/', views.get_reservations_from_flight),

    # Reservation urls
    path('reservations/', views.reservations),
    path('reservations/<int:id>/', views.reservation_detail),

    # Filtering
    path("flights/filter/", views.filter_flights),
]
