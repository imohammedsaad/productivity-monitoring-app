import json
import os
import requests
from database import add_alert, get_alerts

# Path to zones.json (adjust if needed)
ZONES_FILE = os.path.join(os.path.dirname(__file__), '../video_zone/zones.json')
IDLE_THRESHOLD_MINUTES = 15  # You can make this configurable if you want

def load_zones():
    with open(ZONES_FILE, 'r') as f:
        return json.load(f)

def get_zone_info():
    """
    Returns:
        zone_types: dict of zone name -> type
        zone_capacities: dict of zone name -> capacity (if set)
    """
    zones = load_zones()
    zone_types = {}
    zone_capacities = {}
    for z in zones:
        # Use 'label' as the zone name (matches your zone_drawer.py)
        name = z.get('label')
        if name:
            zone_types[name] = z.get('type', '')
            if 'capacity' in z:
                zone_capacities[name] = z['capacity']
    return zone_types, zone_capacities

def get_logs_from_api():
    resp = requests.get("http://localhost:5000/logs")
    if resp.status_code == 200:
        return resp.json()
    return []

def process_logs_for_alerts():
    logs = get_logs_from_api()
    zone_types, zone_capacities = get_zone_info()
    zone_counts = {}

    for log in logs:
        zone = log.get('zone')
        person_id = log.get('id')
        duration = log.get('duration_in_zone', 0)
        anomaly = log.get('anomaly')
        zone_type = zone_types.get(zone, "")

        # Idle alert
        if zone_type == "idle" and duration >= IDLE_THRESHOLD_MINUTES * 60:
            msg = f'Person {person_id} idle in {zone} for {duration//60} minutes.'
            add_alert('idle', msg)

        # Restricted access alert
        if zone_type == "restricted":
            msg = f'Person {person_id} entered restricted zone {zone}.'
            add_alert('restricted', msg)

        # Anomaly alert
        if anomaly:
            msg = f'Anomaly for person {person_id} in {zone}: {anomaly}'
            add_alert('anomaly', msg)

        # Count people per zone for overcapacity
        if zone:
            zone_counts[zone] = zone_counts.get(zone, 0) + 1

    # Overcapacity alert
    for zone, count in zone_counts.items():
        limit = zone_capacities.get(zone)
        if limit and count > limit:
            msg = f'Zone {zone} over capacity: {count} people (limit {limit}).'
            add_alert('overcapacity', msg)

def fetch_alerts():
    return get_alerts()

if __name__ == "__main__":
    process_logs_for_alerts()
    print(list(fetch_alerts()))
