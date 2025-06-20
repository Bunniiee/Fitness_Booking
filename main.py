from fastapi import FastAPI, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
import logging
from typing import List, Optional
from datetime import datetime
from schemas import ClassOut, BookingCreate, BookingOut, ClassCreate
from utils import convert_ist_to_user_tz, IST
from sqlalchemy.exc import SQLAlchemyError
from models import seed_default_classes_from_json
from contextlib import asynccontextmanager

models.Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    seed_default_classes_from_json(db)
    db.close()
    yield

app = FastAPI(title="Fitness Studio Booking API", lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Welcome to the Fitness Studio Booking API!"}

@app.get("/classes", response_model=List[ClassOut])
def get_classes(
    timezone: Optional[str] = Query(None, description="User timezone, e.g. 'Asia/Kolkata'"),
    db: Session = Depends(get_db)
):
    now_ist = datetime.now()
    classes = db.query(models.Class).filter(models.Class.datetime >= now_ist).order_by(models.Class.datetime).all()
    result = []
    for c in classes:
        class_dict = c.__dict__.copy()
        dt = c.datetime
        if timezone:
            dt = convert_ist_to_user_tz(dt, timezone)
        class_dict["datetime"] = dt
        result.append(ClassOut(**class_dict))
    return result 

@app.post("/book", response_model=BookingOut)
def book_class(
    booking: BookingCreate,
    db: Session = Depends(get_db)
):
    # Validate class existence
    fitness_class = db.query(models.Class).filter(models.Class.id == booking.class_id).first()
    if not fitness_class:
        logger.warning(f"Booking failed: Class {booking.class_id} not found.")
        raise HTTPException(status_code=404, detail="Class not found.")
    # Validate available slots
    if fitness_class.available_slots <= 0:
        logger.warning(f"Booking failed: No slots left for class {fitness_class.id}.")
        raise HTTPException(status_code=400, detail="No available slots for this class.")
    # Prevent duplicate booking for same user and class
    existing = db.query(models.Booking).filter(
        models.Booking.class_id == booking.class_id,
        models.Booking.client_email == booking.client_email
    ).first()
    if existing:
        logger.warning(f"Booking failed: Duplicate booking for {booking.client_email} in class {booking.class_id}.")
        raise HTTPException(status_code=400, detail="You have already booked this class.")
    # Create booking
    new_booking = models.Booking(
        class_id=booking.class_id,
        client_name=booking.client_name,
        client_email=booking.client_email
    )
    try:
        fitness_class.available_slots -= 1
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        logger.info(f"Booking successful: {booking.client_email} for class {booking.class_id}.")
        return BookingOut(
            id=new_booking.id,
            class_id=new_booking.class_id,
            client_name=new_booking.client_name,
            client_email=new_booking.client_email,
            booking_time=new_booking.booking_time
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Booking failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Booking failed due to server error.") 

@app.get("/bookings", response_model=List[BookingOut])
def get_bookings(
    email: str = Query(..., description="Client email to filter bookings"),
    db: Session = Depends(get_db)
):
    if not email:
        logger.warning("Bookings fetch failed: Email not provided.")
        raise HTTPException(status_code=400, detail="Email query parameter is required.")
    bookings = db.query(models.Booking).filter(models.Booking.client_email == email).order_by(models.Booking.booking_time.desc()).all()
    logger.info(f"Fetched {len(bookings)} bookings for {email}.")
    return [
        BookingOut(
            id=b.id,
            class_id=b.class_id,
            client_name=b.client_name,
            client_email=b.client_email,
            booking_time=b.booking_time
        ) for b in bookings
    ] 

@app.post("/add_class", response_model=ClassOut)
def add_class(
    class_in: ClassCreate,
    db: Session = Depends(get_db)
):
    new_class = models.Class(
        name=class_in.name,
        datetime=class_in.datetime,
        instructor=class_in.instructor,
        available_slots=class_in.available_slots
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    logger.info(f"Added new class: {new_class.name} at {new_class.datetime}")
    return new_class 