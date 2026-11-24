import os
import time
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException, status
import httpx
from pydantic import BaseModel, Field

app = FastAPI(title="Exam Scheduler Service")


class ExamRequest(BaseModel):
  id: str = Field(..., min_length=1)
  course_code: str = Field(..., min_length=1)
  day: str = Field(..., min_length=1)
  start_hour: int = Field(..., ge=8, le=20)
  end_hour: int = Field(..., ge=8, le=20)
  students: int = Field(..., gt=0)


def get_config_values() -> Dict[str, Any]:
  return {
      "booking_service_url": os.getenv(
          "BOOKING_SERVICE_URL", "http://127.0.0.1:8001"
      ).rstrip("/"),
      "timeout_seconds": float(os.getenv("BOOKING_TIMEOUT_SECONDS", "1.5")),
      "max_retries": int(os.getenv("BOOKING_MAX_RETRIES", "3")),
  }


def overlaps(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
  return a_start < b_end and b_start < a_end


def request_with_retry(
    method: str, url: str, json_data: Dict[str, Any] | None = None
) -> httpx.Response:
  cfg = get_config_values()
  timeout = cfg["timeout_seconds"]
  max_retries = cfg["max_retries"]
  backoff_schedule = [0.5, 1.0, 2.0]

  attempt = 0
  while True:
    try:
      response = httpx.request(
          method=method, url=url, json=json_data, timeout=timeout
      )
      if response.status_code in (404, 409):
        return response
      if response.status_code >= 500:
        raise httpx.HTTPStatusError(
            f"Server error {response.status_code}",
            request=response.request,
            response=response,
        )
      return response
    except (httpx.TimeoutException, httpx.RequestError, httpx.HTTPStatusError):
      if attempt >= max_retries:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Room Booking Service unavailable after retries",
        )
      sleep_time = backoff_schedule[min(attempt, len(backoff_schedule) - 1)]
      attempt += 1
      time.sleep(sleep_time)


@app.get("/config")
def read_config() -> Dict[str, Any]:
  return get_config_values()


@app.post("/exams", status_code=status.HTTP_201_CREATED)
def schedule_exam(exam: ExamRequest) -> Dict[str, Any]:
  cfg = get_config_values()
  base_url = cfg["booking_service_url"]

  rooms_resp = request_with_retry("GET", f"{base_url}/rooms")
  rooms_list: List[Dict[str, Any]] = rooms_resp.json()

  bookings_resp = request_with_retry("GET", f"{base_url}/bookings")
  bookings_list: List[Dict[str, Any]] = bookings_resp.json()

  suitable_rooms = [
      r for r in rooms_list if int(r.get("capacity", 0)) >= exam.students
  ]
  suitable_rooms.sort(key=lambda r: int(r.get("capacity", 0)))

  for room in suitable_rooms:
    room_id = room["id"]
    has_conflict = any(
        b.get("room_id") == room_id
        and b.get("day") == exam.day
        and overlaps(
            exam.start_hour,
            exam.end_hour,
            int(b.get("start_hour", 0)),
            int(b.get("end_hour", 0)),
        )
        for b in bookings_list
    )
    if has_conflict:
      continue

    booking_payload = {
        "room_id": room_id,
        "day": exam.day,
        "start_hour": exam.start_hour,
        "end_hour": exam.end_hour,
        "purpose": f"Exam {exam.id} ({exam.course_code})",
    }
    booking_resp = request_with_retry(
        "PUT", f"{base_url}/bookings/{exam.id}", json_data=booking_payload
    )
    if booking_resp.status_code in (200, 201):
      return {
          "exam_id": exam.id,
          "course_code": exam.course_code,
          "booked_room": room,
          "booking": booking_resp.json(),
      }

  raise HTTPException(
      status_code=status.HTTP_409_CONFLICT,
      detail="No available room large enough for the requested exam time",
  )
