import time
import httpx

URLS = [
    "http://127.0.0.1:8001/health",
    "http://127.0.0.1:8002/health",
    "http://127.0.0.1:8003/health",
]

TIMEOUT_SECONDS = 1.0
SLOW_THRESHOLD_MS = 500.0
INTERVAL_SECONDS = 2.0


def check_service(url: str) -> str:
  start = time.perf_counter()
  try:
    response = httpx.get(url, timeout=TIMEOUT_SECONDS)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    if response.status_code == 200:
      state = "SLOW" if elapsed_ms > SLOW_THRESHOLD_MS else "UP"
      return f"{url} -> {state} ({elapsed_ms:.1f} ms)"
    return f"{url} -> DOWN (HTTP {response.status_code})"
  except httpx.RequestError:
    return f"{url} -> DOWN (no response)"


def main() -> None:
  while True:
    results = [check_service(url) for url in URLS]
    print(" | ".join(results), flush=True)
    time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
  main()
