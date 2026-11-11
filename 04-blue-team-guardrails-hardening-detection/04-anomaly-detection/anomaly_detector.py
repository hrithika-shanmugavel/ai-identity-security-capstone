
from collections import defaultdict, deque
from datetime import datetime
import threading
import time

THRESHOLD = 20
TIME_WINDOW = 60

# Store request timestamps separately for each identity
request_logs = defaultdict(deque)

# Prevent repeated alerts for the same identity
alerted = set()

lock = threading.Lock()


def monitor_api_request(identity):

    with lock:

        current_time = time.monotonic()

        logs = request_logs[identity]

        # Remove requests older than 60 seconds
        while (
            logs
            and current_time - logs[0] > TIME_WINDOW
        ):
            logs.popleft()

        # Record the current request
        logs.append(current_time)

        count = len(logs)

        print(
            f"Request recorded | "
            f"Identity: {identity} | "
            f"Count: {count}"
        )

        # Trigger alert when count exceeds 20
        if count > THRESHOLD and identity not in alerted:

            timestamp = datetime.now().astimezone().strftime(
                "%Y-%m-%d %H:%M:%S %Z"
            )

            print("\n========== SECURITY ALERT ==========")
            print("Timestamp:", timestamp)
            print("Identity:", identity)
            print("Event Type: API_VOLUME_SPIKE")
            print("Requests detected:", count)
            print("Threshold:", THRESHOLD)
            print("Time Window:", TIME_WINDOW, "seconds")
            print("Status: ALERT TRIGGERED")
            print("====================================\n")

            alerted.add(identity)
