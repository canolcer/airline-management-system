"""
1. **index(request)**: Renders the index page (a simple landing page).

2. **Airplane Endpoints**:
   - **airplanes(request)**:
     - **GET**: Returns a list of all airplanes in JSON format.
     - **POST**: Creates a new airplane with data provided in the request body. Validates required fields and ensures the tail number is unique.

   - **airplane_detail(request, id)**:
     - **GET**: Returns details of a specific airplane based on the provided ID.
     - **PATCH**: Updates airplane information if the fields (tail number, model, capacity, production year, status) are valid.
     - **DELETE**: Deletes the specified airplane from the database.

   - **get_flights_from_airplane(request, id)**: Returns a list of all flights associated with a specific airplane.

3. **Flight Endpoints**:
   - **flights(request)**:
     - **GET**: Returns a list of all flights in JSON format.
     - **POST**: Creates a new flight with data provided in the request body. Validates required fields and ensures the flight is associated with a valid airplane.

   - **flight_detail(request, id)**:
     - **GET**: Returns details of a specific flight based on the provided ID.
     - **PATCH**: Updates flight information if the fields (flight number, departure, destination, times, airplane ID) are valid.
     - **DELETE**: Deletes the specified flight from the database.

   - **get_reservations_from_flight(request, id)**: Returns a list of all reservations associated with a specific flight.

4. **Reservation Endpoints**:
   - **reservations(request)**:
     - **GET**: Returns a list of all reservations in JSON format.
     - **POST**: Creates a new reservation with data provided in the request body. Validates required fields and generates a unique reservation code.

   - **reservation_detail(request, id)**:
     - **GET**: Returns details of a specific reservation based on the provided ID.
     - **PATCH**: Updates reservation information if the fields (passenger name, email, reservation code, status, flight) are valid.
     - **DELETE**: Deletes the specified reservation from the database.

5. **Filtering**:
   - **filter_flights(request)**: Filters flights based on query parameters such as departure, destination, and times. Returns a list of matching flights.
"""

from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ValidationError
from .models import Airplane, Flight, Reservation
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import uuid

def index(request):
    return render(request, "index.html")

# Airplane Endpoints
@csrf_exempt
def airplanes(request):
    # If the request method is GET, return all airplanes data.
    if request.method == "GET":
        airplanes = list(Airplane.objects.values())  # Get all airplanes
        return JsonResponse(airplanes, safe=False)

    # If the request method is POST, process the request to create a new airplane.
    elif request.method == "POST":
        try:
            # Parse the JSON data from the request body.
            data = json.loads(request.body)
            
            # Check if all required fields are present in the request data.
            required_fields = ["tail_number", "model", "capacity", "production_year", "status"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                # If any required field is missing, return an error response with missing field names.
                return JsonResponse(
                    {"error": "Missing required fields", "missing_fields": missing_fields}, 
                    status=400
                )
            
            # Check if the tail number already exists in the database.
            if Airplane.objects.filter(tail_number=data["tail_number"]).exists():
                # If the tail number is not unique, return an error response.
                return JsonResponse({"error": "Tail number must be unique"}, status=400)

            # Create a new airplane with the provided data.
            airplane = Airplane.objects.create(
                tail_number=data["tail_number"],
                model=data["model"],
                capacity=data["capacity"],
                production_year=data["production_year"],
                status=data["status"]
            )

            # Return the created airplane's data as a JSON response.
            return JsonResponse({
                "id": airplane.id,
                "tail_number": airplane.tail_number,
                "model": airplane.model,
                "capacity": airplane.capacity,
                "production_year": airplane.production_year,
                "status": airplane.status
            }, status=201)

        except json.JSONDecodeError:
            # If the JSON data is invalid, return an error response.
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    # If the method is neither GET nor POST, return a method not allowed response.
    return JsonResponse({"error": "Method Not Allowed"}, status=405)


@csrf_exempt
def airplane_detail(request, id):
    try:
        # Try to get the airplane by ID. If not found, return a 404 error.
        airplane = get_object_or_404(Airplane, id=id)
    except:
        # If the airplane with the given ID doesn't exist, return an error response.
        return JsonResponse({"error": "No such airplane exists"}, status=404)

    # If the request method is GET, return the details of the specific airplane.
    if request.method == "GET":
        return JsonResponse({
            "id": airplane.id,
            "tail_number": airplane.tail_number,
            "model": airplane.model,
            "capacity": airplane.capacity,
            "production_year": airplane.production_year,
            "status": airplane.status
        })
    
    # If the request method is PATCH, update the airplane's details.
    elif request.method == "PATCH":
        try:
            # Parse the JSON data from the request body.
            data = json.loads(request.body)

            # List of fields that can be updated.
            fields = ["tail_number", "model", "capacity", "production_year", "status"]

            # Iterate through the provided data and update the airplane's attributes.
            for key, value in data.items():
                if key in fields:
                    setattr(airplane, key, value)
            
            # Save the updated airplane data to the database.
            airplane.save()

            # Return the updated airplane's data as a JSON response.
            return JsonResponse({
                "id": airplane.id,
                "tail_number": airplane.tail_number,
                "model": airplane.model,
                "capacity": airplane.capacity,
                "production_year": airplane.production_year,
                "status": airplane.status
            }, status=200)
        
        except json.JSONDecodeError:
            # If the JSON data is invalid, return an error response.
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    # If the request method is DELETE, delete the airplane from the database.
    elif request.method == "DELETE":
        airplane.delete()
        return JsonResponse({"message": "Airplane deleted successfully"}, status=204)

    # If the method is neither GET, PATCH, nor DELETE, return a method not allowed response.
    return JsonResponse({"error": "Method Not Allowed"}, status=405)


def get_flights_from_airplane(request, id):
    # Retrieve the airplane with the given ID or return a 404 error if not found.
    try:
        airplane = get_object_or_404(Airplane, id=id)
    except:
        return JsonResponse({"error": "No such airplane exists"}, status=404)
    
    # Get all flights associated with the retrieved airplane.
    # Select specific fields to return: id, flight number, departure, destination, departure_time, and arrival_time.
    flights = Flight.objects.filter(airplane=airplane).values(
        "id", "flight_number", "departure", "destination", "departure_time", "arrival_time"
    )
    
    # Return the list of flights as a JSON response.
    return JsonResponse(list(flights), safe=False)


# Flight Endpoints
@csrf_exempt
def flights(request):

    # Handle GET request: Retrieve all flight records.
    if request.method == "GET":
        flights = list(Flight.objects.values())  # Get all flights and convert them to a list.
        return JsonResponse(flights, safe=False)  # Return the flights data as a JSON response.
    
    # Handle POST request: Create a new flight record.
    elif request.method == "POST":
        # Parse the incoming JSON request body.
        data = json.loads(request.body)

        # Define the required fields for creating a flight.
        fields = ["flight_number", "departure", "destination", "departure_time", "arrival_time", 
                  "airplane_id"]
        missing_fields = [field for field in fields if field not in data]

        if missing_fields:
            # If any required field is missing, return an error response with missing field names.
            return JsonResponse(
                {"error": "Missing required fields", "missing_fields": missing_fields}, 
                status=400
            )
        
        if Flight.objects.filter(flight_number=data["flight_number"]).exists():
                # If the flight number is not unique, return an error response.
                return JsonResponse({"error": "Flight number must be unique"}, status=400)
        
        # Checks if the given airplane_id exists in the Airplane model.
        if not Airplane.objects.filter(id=data["airplane_id"]).exists():
            return JsonResponse({"error":"No such airplane exists"}, status=400)
        
        # Retrieve the airplane instance based on the provided airplane_id.
        airplane = get_object_or_404(Airplane, id=data["airplane_id"])

        if data.get("reservation_count"):
            reservation_count = data["reservation_count"]
        else:
            reservation_count = 0

        # Create a new flight record with the provided data and associated airplane.
        flight = Flight.objects.create(
                flight_number=data["flight_number"],
                departure=data["departure"],
                destination=data["destination"],
                departure_time=data["departure_time"],
                arrival_time=data["arrival_time"],
                airplane=airplane,
                reservation_count = reservation_count
            )

        # Return the newly created flight's data as a JSON response, including the airplane ID.
        return JsonResponse({
            "id": flight.id,
            "flight_number": flight.flight_number,
            "departure": flight.departure,
            "destination": flight.destination,
            "departure_time": flight.departure_time,
            "arrival_time": flight.arrival_time,
            "airplane_id": flight.airplane.id,  # ForeignKey ID linking to the Airplane model.
            "reservation_count": flight.reservation_count
        }, status=201)

    # Return error if the HTTP method is not GET or POST.
    return JsonResponse({"error": "Method Not Allowed"}, status=405)


@csrf_exempt
def flight_detail(request, id):
    # Try to retrieve the flight with the given id. If not found, return a 404 error.
    try:
        flight = get_object_or_404(Flight, id=id)
    except:
        return JsonResponse({"error": "No such flight exists"}, status=404)

    # Handle GET request: Return the details of the flight.
    if request.method == "GET":
        return JsonResponse({
            "id": flight.id,
            "flight_number": flight.flight_number,
            "departure": flight.departure,
            "destination": flight.destination,
            "departure_time": flight.departure_time,
            "arrival_time": flight.arrival_time,
            "airplane": flight.airplane.tail_number  # Returning the airplane's tail number
        })
    
    # Handle PATCH request: Update the flight details.
    elif request.method == "PATCH":
        try:
            # Parse the incoming JSON data.
            data = json.loads(request.body)

            # Define the fields that can be updated.
            fields = ["flight_number", "departure", "destination", "departure_time", "arrival_time", 
                      "airplane_id", "reservation_count"]
            
            # Update the flight attributes with the data provided in the request.
            for key, value in data.items():
                if key in fields:
                    setattr(flight, key, value)
            
            # Save the updated flight record.
            flight.save()
            
            # Return the updated flight details.
            return JsonResponse({
                "id": flight.id,
                "flight_number": flight.flight_number,
                "departure": flight.departure,
                "destination": flight.destination,
                "departure_time": flight.departure_time,
                "arrival_time": flight.arrival_time,
                "airplane": flight.airplane.tail_number,  # Returning the airplane's tail number
                "reservation_count": flight.reservation_count
            })

        # Handle invalid JSON data format.
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    # Handle DELETE request: Delete the flight record.
    elif request.method == "DELETE":
        flight.delete()  # Delete the flight from the database.
        return JsonResponse({"message": "Flight deleted successfully."}, status=204)

    # Return error if the HTTP method is not GET, PATCH, or DELETE.
    return JsonResponse({"error": "Method Not Allowed"}, status=405)


def get_reservations_from_flight(request, id):
    # Retrieve the flight object with the given id. If not found, return a 404 error.
    try:
        flight = get_object_or_404(Flight, id=id)
    except:
        return JsonResponse({"error": "No such flight exists"}, status=404)

    # Retrieve the reservations related to the specified flight and select relevant fields.
    reservations = Reservation.objects.filter(flight=flight).values(
        "id", "passenger_name", "passenger_email", "reservation_code", "status", "created_at"
    )
    
    # Return the list of reservations in JSON format.
    return JsonResponse(list(reservations), safe=False)



# Reservation endpoints
@csrf_exempt
def reservations(request):

    # Handle GET request to retrieve all reservations.
    if request.method == "GET":
        # Fetch all reservation records and return them in JSON format.
        reservations = list(Reservation.objects.values())
        return JsonResponse(reservations, safe=False)
    
    # Handle POST request to create a new reservation.
    elif request.method == "POST":
        # Parse the incoming JSON data from the request body.
        data = json.loads(request.body)

        # List of required fields for creating a reservation.
        required_fields = ["passenger_name", "passenger_email", "flight_id", "status"]
        missing_fields = [field for field in required_fields if field not in data]

        # Check if all required fields are present in the data.
        if not all(field in data for field in required_fields):
            return JsonResponse(
                {"error": "Missing required fields", "missing_fields": missing_fields}, 
                status=400
            )
        
        # Fetch the flight object based on the provided flight_id.
        try:
            flight = get_object_or_404(Flight, id=data["flight_id"])
        except:
            return JsonResponse({"error": "No such flight exists"}, status=404)


        # Get the reservation code from the data or generate one if not provided.
        reservation_code = data.get("reservation_code")
        created_at = timezone.now()

        # If no reservation code is provided, generate a unique code.
        if not reservation_code:
            while True:
                reservation_code = str(uuid.uuid4())[:8]  # Generate an 8-character code
                # Ensure that the generated reservation code does not already exist in the database.
                if not Reservation.objects.filter(reservation_code=reservation_code).exists():
                    break  # Exit the loop once a unique code is found

        # Create a new reservation object in the database.
        try:
            reservation = Reservation.objects.create(
                    passenger_name=data["passenger_name"],
                    passenger_email=data["passenger_email"],
                    reservation_code=reservation_code,
                    flight=flight,
                    status=data["status"],
                    created_at=created_at
                )
        except ValidationError:
            return JsonResponse({"error": "Reservation is fully booked!"}, status=404)
            

        # Return the details of the created reservation in JSON format with status 201.
        return JsonResponse({
            "id": reservation.id,
            "passenger_name": reservation.passenger_name,
            "passenger_email": reservation.passenger_email,
            "reservation_code": reservation.reservation_code,
            "flight_id": reservation.flight.id,
            "status": reservation.status,
            "created_at": reservation.created_at
        }, status=201)

    # Return a 405 error for unsupported HTTP methods.
    return JsonResponse({"error": "Method Not Allowed"}, status=405)


@csrf_exempt
def reservation_detail(request, id):
    # Try to retrieve the reservation object by its ID, return 404 if not found.
    try:
        reservation = get_object_or_404(Reservation, id=id)
    except:
        return JsonResponse({"error": "No such reservation exists"}, status=404)

    # Handle GET request to fetch the details of the reservation.
    if request.method == "GET":
        return JsonResponse({
            "id": reservation.id,
            "passenger_name": reservation.passenger_name,
            "passenger_email": reservation.passenger_email,
            "reservation_code": reservation.reservation_code,
            "flight": reservation.flight.flight_number,  # Return the flight number.
            "status": reservation.status,
            "created_at": reservation.created_at
        })
    
    # Handle PATCH request to update reservation details.
    elif request.method == "PATCH":
        try:
            # Parse the incoming JSON data from the request body.
            data = json.loads(request.body)

            # List of fields that can be updated.
            fields = ["passenger_name", "passenger_email", "reservation_code", "flight_id", "status"]

            # Check if the provided reservation code already exists in the database (excluding current reservation).
            if "reservation_code" in data:
                if Reservation.objects.exclude(id=id).filter(reservation_code=data["reservation_code"]).exists():
                    return JsonResponse({"error": "Reservation code must be unique"}, status=400)
            
            # If flight_id is provided, validate and assign the new flight to the reservation.
            if "flight_id" in data:
                flight = Flight.objects.filter(id=data["flight_id"]).first()
                if flight:
                    reservation.flight = flight  # Update the flight associated with the reservation.
                else:
                    return JsonResponse({"error": "Invalid flight_id"}, status=400)
            
            # Update other fields in the reservation.
            for key, value in data.items():
                if key in fields:
                    setattr(reservation, key, value)
            
            # Save the updated reservation object.
            reservation.save()
            
            # Return the updated reservation details.
            return JsonResponse({
                "id": reservation.id,
                "passenger_name": reservation.passenger_name,
                "passenger_email": reservation.passenger_email,
                "reservation_code": reservation.reservation_code,
                "flight": reservation.flight.flight_number,
                "status": reservation.status,
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    # Return a 405 error for unsupported HTTP methods.
    return JsonResponse({"error": "Method Not Allowed"}, status=405)


# Filtering
def filter_flights(request):
    # Get the query parameters from the GET request.
    departure = request.GET.get("departure")
    destination = request.GET.get("destination")
    departure_time = request.GET.get("departure_time")
    arrival_time = request.GET.get("arrival_time")

    # Start by retrieving all flights.
    flights = Flight.objects.all()

    # Apply filters based on the query parameters, if provided.
    if departure:
        # Filter by departure location (case-insensitive partial match).
        flights = flights.filter(departure__icontains=departure)
    if destination:
        # Filter by destination location (case-insensitive partial match).
        flights = flights.filter(destination__icontains=destination)
    if departure_time:
        # Filter by departure time.
        flights = flights.filter(departure_time=departure_time)
    if arrival_time:
        # Filter by arrival time.
        flights = flights.filter(arrival_time=arrival_time)

    # Prepare the list of filtered flights to return in the response.
    data = [
        {
            "id": flight.id,
            "departure": flight.departure,
            "arrival": flight.destination,
            "departure_time": flight.departure_time,
            "arrival_time": flight.arrival_time,
        }
        for flight in flights
    ]

    # Return the filtered flights in JSON format.
    return JsonResponse({"flights": data}, safe=False)
