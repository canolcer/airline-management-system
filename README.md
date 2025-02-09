# ✈️ Airline Reservation System

## 📌 Overview
This is a **Django-based airline reservation system** that allows users to:
- Manage **airplanes**, **flights**, and **reservations** via a RESTful API.
- Ensure **basic validation** on input data to prevent errors.
- Automatically track **flight reservation counts** using Django signals.
- Send **confirmation emails** upon successful reservations.

📌 **If the user enters their email address while making a reservation, they will receive a confirmation email.**

## 📂 Project Structure
```md
airline-management-system/
│── airline_management_system/
│   ├── __init__.py       # Project initialization
│   ├── asgi.py           # ASGI config for deployment
│   ├── settings.py       # Project settings and configurations
│   ├── urls.py           # URL routing for the entire project
│   ├── wsgi.py           # WSGI config for deployment
│
│── airline/
│   ├── __init__.py       # App initialization
│   ├── admin.py          # Django admin panel settings
│   ├── apps.py           # App configuration
│   ├── models.py         # Database models for airplanes, flights, and reservations
│   ├── signals.py        # Signals to update flight reservation counts
│   ├── tests.py          # Unit tests for the application
│   ├── views.py          # API views handling GET, POST, PATCH, DELETE requests
│
│── templates/            # HTML templates for the project
│── db.sqlite3            # SQLite database file
│── manage.py             # Django's management script
│── README.md             # Documentation
```

---

## 🚀 Installation & Setup
### 1️⃣ Clone the Repository
#### Option 1: Using Git
```sh
git clone https://github.com/canolcer/airline-management-system.git
cd airline-management-system

```
#### Option 2: Using zip file
Extract the ZIP file to your desired location.
```

```
### 2️⃣ Apply Migrations
```sh
python manage.py makemigrations
python manage.py migrate
```

### 3️⃣ Run the Development Server
```sh
python manage.py runserver
```

Now, the API will be available at: `http://127.0.0.1:8000/`

---

## 📡 API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/airplanes/` | GET | Get all airplanes |
| `/airplanes/` | POST | Add a new airplane |
| `/airplanes/<id>/` | GET | Get airplane details |
| `/airplanes/<id>/flights/` | GET | Get flights from a specific airplane |
| `/flights/` | GET | Get all flights |
| `/flights/` | POST | Create a new flight |
| `/flights/<id>/` | GET | Get flight details |
| `/flights/<id>/reservations/` | GET | Get reservations for a flight |
| `/reservations/` | GET | Get all reservations |
| `/reservations/` | POST | Create a new reservation |
| `/reservations/<id>/` | GET | Get reservation details |
| `/flights/filter/?departure=city` | GET | Filter flights based on criteria |

📌 **All requests should be made using JSON format.**

---

## 🔍 API Testing with Postman
1. Import the provided **Postman Collection** (`airline_postman_collection.json`).
2. Update the base URL in Postman (`http://127.0.0.1:8000/`).
3. Test each endpoint using the defined requests.

---

## ✅ Basic Validation
- Airplane `capacity` must be **greater than 0**.
- Unique constraints:
  - Airplane `tail_number`
  - Flight `flight_number`
  - Reservation `reservation_code`
- If a flight is **fully booked**, new reservations will be rejected.

📌 **When making a reservation, if the user enters their email address, a confirmation email will be sent to them.**

---

