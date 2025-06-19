# Fitness Studio Booking API

A FastAPI backend for managing fitness class schedules and bookings.

---

## Features
- View upcoming fitness classes
- Book a class (with slot validation)
- View bookings by user email
- Add new classes (for development/testing)
- Timezone support (classes stored in IST, can be viewed in any timezone)

---

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Fitness_Booking
   ```

2. **Install dependencies**
   ```bash
   python -m pip install fastapi uvicorn sqlalchemy pydantic email-validator pytz
   ```

3. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

4. **Open Swagger UI**
   - Go to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.
   - You can interact with all API endpoints here.

---

## API Endpoints & Usage

### 1. **Add a Class**
- **POST** `/add_class`
- **Body Example:**
  ```json
  {
    "name": "Yoga Morning",
    "datetime": "2024-06-10T07:00:00",
    "instructor": "Alice",
    "available_slots": 10
  }
  ```
- **Description:** Adds a new class. Use this before booking.

### 2. **View Upcoming Classes**
- **GET** `/classes`
- **Query (optional):** `timezone` (e.g., `Asia/Kolkata`, `UTC`, etc.)
- **Description:** Lists all upcoming classes. Times are in IST by default, or converted to your timezone if provided.

### 3. **Book a Class**
- **POST** `/book`
- **Body Example:**
  ```json
  {
    "class_id": 1,
    "client_name": "John Doe",
    "client_email": "john@example.com"
  }
  ```
- **Description:** Books a class for a user. Validates available slots and prevents duplicate bookings.

### 4. **View Bookings by Email**
- **GET** `/bookings?email=client@example.com`
- **Description:** Lists all bookings made by the specified email address.

---

## Notes
- All class times are stored in IST (Asia/Kolkata). Use the `timezone` query param in `/classes` to view in your local timezone.
- The `/add_class` endpoint is for development/testing. Remove or secure it before production.
- Data is stored in a file-based SQLite database (`fitness_booking.db`).

---

## Troubleshooting
- If you see import errors, ensure you installed all dependencies in the correct Python environment.
- Use `python -m pip install ...` to avoid environment issues.

---

## License
MIT 