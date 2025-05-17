import requests

BACKEND_URL = 'http://localhost:5000'

def get_alerts():
    resp = requests.get(f'{BACKEND_URL}/alerts')
    return resp.json()

def get_contacts():
    resp = requests.get(f'{BACKEND_URL}/contacts')
    return resp.json()

def get_stats():
    resp = requests.get(f'{BACKEND_URL}/stats')
    return resp.json()

def export_logs():
    resp = requests.get(f'{BACKEND_URL}/export')
    with open('logs_export.csv', 'wb') as f:
        f.write(resp.content)
    return 'logs_export.csv'

if __name__ == "__main__":
    print(get_alerts())
    print(get_contacts())
    print(get_stats())
