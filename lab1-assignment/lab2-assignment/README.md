# Lab Assignment 2: A Campus Room Booking Service

## Step 1: API Design Table
| Operation | Method | URI | Request Body | Success Status | Error Status Codes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Create Room | `POST` | `/rooms` | `{"id": "B205", "building": "Main", "capacity": 30}` | `201 Created` | `409 Conflict`, `422 Unprocessable Entity` |
| List Rooms | `GET` | `/rooms` | None | `200 OK` | None |
| Get Room | `GET` | `/rooms/{room_id}` | None | `200 OK` | `404 Not Found` |
| Create/Retry Booking | `PUT` | `/bookings/{booking_id}` | `{"room_id": "B205", "day": "2026-11-25", "start_hour": 10, "end_hour": 12, "purpose": "Lab session"}` | `200 OK` | `404 Not Found`, `409 Conflict`, `422 Unprocessable Entity` |
| Cancel Booking | `DELETE` | `/bookings/{booking_id}` | None | `204 No Content` | `404 Not Found` |

## Step 3: Client Script Output (`test_bookings.py`)
```text
Create room B205: 201
Duplicate room B205: 409
Get unknown room: 404
Invalid booking hours: 422
Booking unknown room: 404
Create booking bk-101 (1st try): 200
Retry same booking bk-101 (2nd try): 200
Overlapping booking bk-102: 409
Adjacent booking bk-103 (12-13): 200
