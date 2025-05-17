import requests
import json

BACKEND_URL = 'http://localhost:5000/log'

def send_log(data, url=BACKEND_URL):
    try:
        resp = requests.post(url, json=data)
        print(f"Sent log: {data}, Response: {resp.status_code}")
        return resp.status_code
    except Exception as e:
        print(f"Error sending log: {e}")
        return None

def send_logs_batch(logs, url=BACKEND_URL):
    # logs: list of dicts
    for log in logs:
        send_log(log, url)

if __name__ == "__main__":
    # Test sending a batch of logs
    logs = [
        {'id': 1, 'zone': 'Zone 1', 'timestamp': '2023-01-01T12:00:00'},
        {'id': 2, 'zone': 'Zone 2', 'timestamp': '2023-01-01T12:01:00'}
    ]
    send_logs_batch(logs)
