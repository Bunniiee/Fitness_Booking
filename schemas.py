from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class ClassBase(BaseModel):
    name: str
    datetime: datetime
    instructor: str
    available_slots: int

class ClassOut(ClassBase):
    id: int
    class Config:
        orm_mode = True

class BookingBase(BaseModel):
    class_id: int
    client_name: str
    client_email: EmailStr

class BookingCreate(BookingBase):
    pass

class BookingOut(BookingBase):
    id: int
    booking_time: datetime
    class Config:
        orm_mode = True

class ClassCreate(BaseModel):
    name: str
    datetime: datetime
    instructor: str
    available_slots: int 