# Lab Assignment 3: The Exam Scheduler Service

## Commands to Run Both Services (on Different Ports)
Run the Room Booking Service on port `8001`:
```bash
BOOKING_DELAY_SECONDS=0 uvicorn booking_service:app --host 127.0.0.1 --port 8001
