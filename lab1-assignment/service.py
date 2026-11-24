import time
from fastapi import FastAPI

app = FastAPI()
start_time = time.time()


@app.get("/health")
def health():
  uptime_seconds = round(time.time() - start_time, 2)
  return {"status": "ok", "uptime_seconds": uptime_seconds}
