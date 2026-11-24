import os
import time
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, model_validator

app = FastAPI(title="Campus Room Booking Service")


class RoomCreate(BaseModel):
  id: str = Field(..., min_length=1)
  building: str = Field(..., min_length=1)
  capacity: int = Field(..., gt=0)


class Room(RoomCreate):
  pass


class BookingInput(BaseModel):
  room_id: str = Field(..., min_length=1)
  day: str = Field(..., min_length=1)
  start_hour: int = Field(..., ge=8, le=20)
  end_hour: int = Field(..., ge=8, le=20)
  purpose: str = Field(..., min_length=1)

  @model_validator(mode="after")
  def validate_hours(self) -> "BookingInput":
    if self.end_hour <= self.start_hour:
      raise ValueError("end_hour must be greater than start_hour")
    return self


class Booking(BookingInput):
  id: str


rooms: Dict[str, Room] = {
    "B101": Room(id="B101", building="Main", capacity=25),
    "B205": Room(id="B205", building="Main", capacity=40),
    "A301": Room(id="A301", building="Engineering", capacity=80),
}
bookings: Dict[str, Booking] = {}


def apply_configured_delay() -> None:
  delay = float(os.getenv("BOOKING_DELAY_SECONDS", "0"))
  if delay > 0:
    time.sleep(delay)


def overlaps(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
  return a_start < b_end and b_start < a_end


@app.post("/rooms", response_model=Room, status_code=status.HTTP_201_CREATED)
def create_room(room: RoomCreate) -> Room:
  apply_configured_delay()
  if room.id in rooms:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT, detail="Room already exists"
    )
  created = Room(**room.model_dump())
  rooms[room.id] = created
  return created


@app.get("/rooms", response_model=List[Room])
def list_rooms() -> List[Room]:
  apply_configured_delay()
  return list(rooms.values())


@app.put("/bookings/{booking_id}", response_model=Booking)
def upsert_booking(booking_id: str, payload: BookingInput) -> Booking:
  apply_configured_delay()
  if payload.room_id not in rooms:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
    )

  if booking_id in bookings:
    existing = bookings[booking_id]
    if (
        existing.room_id == payload.room_id
        and existing.day == payload.day
        and existing.start_hour == payload.start_hour
        and existing.end_hour == payload.end_hour
        and existing.purpose == payload.purpose
    ):
      return existing
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Booking ID already used with different details",
    )

  for existing in bookings.values():
    if existing.room_id == payload.room_id and existing.day == payload.day:
      if overlaps(
          payload.start_hour,
          payload.end_hour,
          existing.start_hour,
          existing.end_hour,
      ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Booking overlaps with an existing booking",
        )

  created = Booking(id=booking_id, **payload.model_dump())
  bookings[booking_id] = created
  return created


@app.get("/bookings", response_model=List[Booking])
def list_bookings(room_id: Optional[str] = None) -> List[Booking]:
  apply_configured_delay()
  if room_id is not None:
    return [b for b in bookings.values() if b.room_id == room_id]
  return list(bookings.values())
