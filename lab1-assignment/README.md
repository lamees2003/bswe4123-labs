# Lab Assignment 1: Is the Service Up, Slow or Down?

## Monitor Output (1-Minute Observation)
- `http://127.0.0.1:8001/health -> UP (12.4 ms) | http://127.0.0.1:8002/health -> UP (11.8 ms) | http://127.0.0.1:8003/health -> UP (13.1 ms)`
- `http://127.0.0.1:8001/health -> DOWN (no response) | http://127.0.0.1:8002/health -> SLOW (804.2 ms) | http://127.0.0.1:8003/health -> UP (12.0 ms)`
- `http://127.0.0.1:8001/health -> UP (15.6 ms) | http://127.0.0.1:8002/health -> SLOW (803.9 ms) | http://127.0.0.1:8003/health -> UP (11.5 ms)`

## Step 3 Explanation: Stopping, Restarting, and Slowing Services
- When a service instance is stopped using `Ctrl+C`, the monitor immediately detects that no response is returned and marks it as `DOWN`.
- When that service instance is started again, the next health check succeeds quickly and its status returns to `UP`.
- When another service instance waits `0.8` seconds (`800 ms`) before responding to `/health`, its response time exceeds the `500 ms` threshold, so the monitor reports it as `SLOW`.

## Step 4 Explanation: Consecutive Failure Threshold and Timeout Trade-offs
- A single failed check can happen due to a brief network hiccup or momentary load spike, so requiring multiple consecutive failed checks (for example, 3 failed checks in a row) before marking a service as `DOWN` prevents false alarms.
- Choosing a `1.0s` timeout and a `3`-check consecutive failure threshold balances responsiveness and stability:
  - **What we gain:** Fewer false `DOWN` alerts during temporary slowdowns or brief packet delays.
  - **What we lose:** It takes longer to declare a genuinely crashed service as `DOWN` (for example, around 6 seconds across 2-second intervals).
