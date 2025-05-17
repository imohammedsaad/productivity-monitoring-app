from database import add_alert, get_alerts
from datetime import datetime

def idle_alert(person_id, duration):
    msg = f'Person {person_id} idle for {duration} minutes.'
    add_alert('idle', msg)

def overcapacity_alert(zone, count):
    msg = f'Zone {zone} over capacity: {count} people.'
    add_alert('overcapacity', msg)

def restricted_access_alert(person_id, zone):
    msg = f'Person {person_id} entered restricted zone {zone}.'
    add_alert('restricted', msg)

def fetch_alerts():
    return get_alerts()

if __name__ == "__main__":
    idle_alert(1, 15)
    overcapacity_alert('Zone 1', 12)
    restricted_access_alert(2, 'Zone 3')
    print(list(fetch_alerts()))
