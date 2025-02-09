"""
This module contains Django signals to automatically update the reservation count 
for a flight whenever a reservation is created or deleted.

- When a new reservation is created (`post_save` signal), the `reservation_count` 
  of the associated flight is incremented.
- When a reservation is deleted (`post_delete` signal), the `reservation_count` 
  of the associated flight is decremented.

These signals help maintain an accurate count of reservations for each flight.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Reservation

@receiver(post_save, sender=Reservation)
def update_reservation_count_on_save(sender, instance, created, **kwargs):
    """
    Increments the reservation count for a flight when a new reservation is created.
    """
    if created:
        flight = instance.flight
        flight.reservation_count += 1
        flight.save()

@receiver(post_delete, sender=Reservation)
def update_reservation_count_on_delete(sender, instance, **kwargs):
    """
    Decrements the reservation count for a flight when a reservation is deleted.
    """
    flight = instance.flight
    flight.reservation_count -= 1
    flight.save()
