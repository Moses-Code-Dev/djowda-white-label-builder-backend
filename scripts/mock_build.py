import time
import json
import requests
import sys
from datetime import datetime

# Cloudflare Worker URL (Make sure it's correct)
CLOUDFLARE_LOG_URL = "https://my-worker.mosescodedev.workers.dev/log"

def send_log(event: str, app_name: str = None, status: str = None):
    """
    Sends log data to Cloudflare and prints it to the console.
    """
    log_data = {
        "event": event,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    if app_name:
        log_data["app_name"] = app_name
    if status:
        log_data["status"] = status

    # Print log to VM console
    print(json.dumps(log_data), flush=True)

    # Send log to Cloudflare Worker
    try:
        response = requests.post(CLOUDFLARE_LOG_URL, json=log_data, timeout=5)
        if response.status_code != 200:
            print(f"Cloudflare log failed: {response.status_code} - {response.text}", file=sys.stderr)
    except requests.exceptions.RequestException as e:
        print(f"Failed to send log to Cloudflare: {e}", file=sys.stderr)

def mock_build(app_names):
    """
    Simulates the build process for multiple apps, sending logs at each step.
    """
    send_log("build_started")

    for app in app_names:
        time.sleep(4)  # Simulate build delay
        send_log("app_build", app_name=app, status="success")

    send_log("build_completed")

if __name__ == "__main__":
    # Simulating input from Cloudflare
    sample_input = {
        "user_app": "User App",
        "store_manager_app": "Store Manager App",
        "delivery_app": "Delivery App"
    }

    app_names = list(sample_input.values())
    mock_build(app_names)
