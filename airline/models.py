"""
This Django models file defines the structure for an airline reservation system. It includes:
- Airplane model: Represents an airplane with attributes like tail number, model, capacity, production year, and status.
- Flight model: Represents a flight with attributes like flight number, departure, destination, departure and arrival times, related airplane, and reservation count.
- Reservation model: Represents a passenger's reservation with attributes like passenger name, email, reservation code, associated flight, and reservation status. It also sends a confirmation email upon reservation creation.

Validator functions are included to ensure valid production years and capacities for airplanes, as well as to ensure that a flight is not overbooked. 
"""


from django.core.exceptions import ValidationError
from django.db import models
import uuid
from django.core.mail import send_mail
from airline_management_system import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from socket import gaierror
from django.http import JsonResponse


# Validator function to ensure the year is within a valid range (between 1900 and 2100)
def validate_year(year):
    # Check if the year is less than 1900 or greater than 2100
    if year < 1900 or year > 2100:
        raise ValidationError('Year must be between 1900 and 2100')  # Raise an error if year is invalid

# Validator function to ensure the airplane capacity is greater than zero
def validate_capacity(capacity):
    # Check if the capacity is less than 1
    if capacity < 1:
        raise ValidationError("Capacity can't be 0 or negative")  # Raise an error if capacity is invalid

# Function to generate a unique 8-character reservation code using UUID
def generate_reservation_code():
    # Generate a UUID and slice it to get the first 8 characters for the reservation code
    return str(uuid.uuid4())[:8]

class Airplane(models.Model):
    tail_number = models.CharField(max_length=50, unique=True)
    model = models.TextField()
    capacity = models.IntegerField(validators=[validate_capacity])
    
    # Validator is applied to ensure the year is between 1900 and 2100
    production_year = models.IntegerField(validators=[validate_year])
    status = models.BooleanField()

    def __str__(self):
        return self.tail_number

class Flight(models.Model):
    flight_number = models.CharField(max_length=50, unique=True)  # Unique flight number for each flight
    departure = models.TextField()  # Departure location (city/airport)
    destination = models.TextField()  # Destination location (city/airport)
    departure_time = models.DateTimeField()  # Scheduled departure time
    arrival_time = models.DateTimeField()  # Scheduled arrival time
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name='flights')  # Associated airplane for the flight

    # The reservation count tracks how many reservations have been made for this flight.
    # It helps in determining if the flight is fully booked or not.
    reservation_count = models.IntegerField(default=0)  # Default value set to 0
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Proceed with the normal save operation

    def __str__(self):
        return self.flight_number  # Return the flight number as the string representation of the object

class Reservation(models.Model):
    passenger_name = models.TextField()  # Passenger's name for the reservation
    passenger_email = models.EmailField()  # Passenger's email address
    reservation_code = models.CharField(max_length=50, unique=True, default=generate_reservation_code)  # Unique reservation code, generated automatically
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='reservations')  # The flight associated with this reservation
    status = models.BooleanField()  # Status of the reservation (e.g., confirmed, canceled)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the reservation was created
    
    def save(self, *args, **kwargs):
        # Check if the flight is already fully booked before saving the reservation
        if self.flight.reservation_count >= self.flight.airplane.capacity:
            raise ValidationError("This flight is fully booked!")  # Raise an error if the flight is full
        
        super().save(*args, **kwargs)  # Save the reservation if the flight is not fully booked

        try:
            # Generate the email content using an HTML template
            subject = "Your Flight Reservation Confirmation"  # Subject of the confirmation email
            html_message = render_to_string("reservation_email.html", {  # Render the HTML message using the template
                "flight_number": self.flight.flight_number,  # Flight number
                "departure": self.flight.departure,  # Departure location
                "destination": self.flight.destination,  # Destination location
                "reservation_code": self.reservation_code,  # Unique reservation code
                "passenger_name": self.passenger_name  # Passenger's name
            })
            plain_message = strip_tags(html_message)  # Convert HTML to plain text for email body
            
            send_mail(
                subject,
                plain_message,  # Send plain text version of the email content
                settings.DEFAULT_FROM_EMAIL,  # Sender's email address (defined in settings)
                [self.passenger_email],  # Recipient's email address
                fail_silently=False,  # Do not suppress errors during email sending
                html_message=html_message,  # Send HTML version of the email
            )
        except gaierror:
            return JsonResponse({
        "error": "Reservation has been created and saved in the database; however, the email couldn't be sent. Please check your internet connection"
    }, status=500)
    def __str__(self):
        return f"{self.passenger_name} - {self.reservation_code}"  # String representation of the reservation (passenger name and code)
