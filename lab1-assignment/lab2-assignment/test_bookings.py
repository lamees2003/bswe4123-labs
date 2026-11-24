import httpx
from fastapi.testclient import TestClient
from service import app

client = TestClient(app)


def run_tests() -> None:
  # 1. Create a room (Success 201)
  r1 = client.post(
      "/rooms", json={"id": "B205", "building": "Main", "capacity": 30}
  )
  print("Create room B205:", r1.status_code)

  # 2. Duplicate room (Conflict 409)
  r2 = client.post(
      "/rooms", json={"id": "B205", "building": "Main", "capacity": 30}
  )
  print("Duplicate room B205:", r2.status_code)

  # 3. Unknown room lookup (Not Found 404)
  r3 = client.get("/rooms/UNKNOWN")
  print("Get unknown room:", r3.status_code)

  # 4. Invalid hours: end_hour before start_hour (Unprocessable Entity 422)
  r4 = client.put(
      "/bookings/bk-1",
      json={
          "room_id": "B205",
          "day": "2026-11-25",
          "start_hour": 14,
          "end_hour": 12,
          "purpose": "Study group",
      },
  )
  print("Invalid booking hours:", r4.status_code)

  # 5. Booking for unknown room (Not Found 404)
  r5 = client.put(
      "/bookings/bk-2",
      json={
          "room_id": "NO_ROOM",
          "day": "2026-11-25",
          "start_hour": 10,
          "end_hour": 12,
          "purpose": "Meeting",
      },
  )
  print("Booking unknown room:", r5.status_code)

  # 6. Valid booking creation (Success 200)
  payload = {
      "room_id": "B205",
      "day": "2026-11-25",
      "start_hour": 10,
      "end_hour": 12,
      "purpose": "Lab session",
  }
  r6 = client.put("/bookings/bk-101", json=payload)
  print("Create booking bk-101 (1st try):", r6.status_code)

  # 7. Idempotent retry: sending the exact same request again
  r7 = client.put("/bookings/bk-101", json=payload)
  print("Retry same booking bk-101 (2nd try):", r7.status_code)

  # 8. Overlapping booking on same room & day (Conflict 409)
  r8 = client.put(
      "/bookings/bk-102",
      json={
          "room_id": "B205",
          "day": "2026-11-25",
          "start_hour": 11,
          "end_hour": 13,
          "purpose": "Overlap test",
      },
  )
  print("Overlapping booking bk-102:", r8.status_code)

  # 9. Adjacent non-overlapping booking 12 to 13 (Success 200)
  r9 = client.put(
      "/bookings/bk-103",
      json={
          "room_id": "B205",
          "day": "2026-11-25",
          "start_hour": 12,
          "end_hour": 13,
          "purpose": "Back-to-back session",
      },
  )
  print("Adjacent booking bk-103 (12-13):", r9.status_code)


if __name__ == "__main__":
  run_tests()
