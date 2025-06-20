from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session
from database import Base
import datetime
import json
from pathlib import Path

class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    datetime = Column(DateTime, nullable=False)  # stored as UTC
    instructor = Column(String, nullable=False)
    available_slots = Column(Integer, nullable=False)
    bookings = relationship("Booking", back_populates="fitness_class")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    client_name = Column(String, nullable=False)
    client_email = Column(String, nullable=False)
    booking_time = Column(DateTime, default=datetime.datetime.utcnow)
    fitness_class = relationship("Class", back_populates="bookings")

def seed_default_classes_from_json(db: Session, json_path="default_classes.json"):
    if db.query(Class).count() == 0:
        file_path = Path(json_path)
        if file_path.exists():
            with open(file_path, "r") as f:
                class_list = json.load(f)
                for c in class_list:
                    db.add(Class(
                        name=c["name"],
                        datetime=datetime.datetime.fromisoformat(c["datetime"]),
                        instructor=c["instructor"],
                        available_slots=c["available_slots"]
                    ))
                db.commit() 