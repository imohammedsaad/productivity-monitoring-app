import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '../backend/productivity.db')
ZONES_FILE = os.path.join(os.path.dirname(__file__), '../zones.json')

def get_zone_types():
    with open(ZONES_FILE, 'r') as f:
        zones = json.load(f)
    # Map: zone name/label -> type
    return {z.get('label', z.get('name')): z.get('type', '') for z in zones}

def get_logs_for_person(person_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT zone, timestamp FROM logs WHERE person_id=? ORDER BY timestamp', (person_id,))
    logs = c.fetchall()
    conn.close()
    return logs

def calculate_productive_hours(person_id):
    zone_types = get_zone_types()
    logs = get_logs_for_person(person_id)
    productive_seconds = 0
    last_time = None
    last_zone = None
    for zone, ts in logs:
        t = datetime.fromisoformat(ts)
        if last_time and last_zone:
            delta = (t - last_time).total_seconds()
            if zone_types.get(last_zone) == "active":
                productive_seconds += delta
        last_time = t
        last_zone = zone
    return productive_seconds / 3600  # hours

def calculate_meeting_hours(person_id):
    zone_types = get_zone_types()
    logs = get_logs_for_person(person_id)
    meeting_seconds = 0
    last_time = None
    last_zone = None
    for zone, ts in logs:
        t = datetime.fromisoformat(ts)
        if last_time and last_zone:
            delta = (t - last_time).total_seconds()
            if zone_types.get(last_zone) == "meeting":
                meeting_seconds += delta
        last_time = t
        last_zone = zone
    return meeting_seconds / 3600  # hours

def calculate_break_times(person_id):
    zone_types = get_zone_types()
    logs = get_logs_for_person(person_id)
    break_seconds = 0
    last_time = None
    last_zone = None
    for zone, ts in logs:
        t = datetime.fromisoformat(ts)
        if last_time and last_zone:
            delta = (t - last_time).total_seconds()
            if zone_types.get(last_zone) == "idle":
                break_seconds += delta
        last_time = t
        last_zone = zone
    return break_seconds / 60  # minutes

def calculate_collaborative_times():
    # Returns: {zone: number_of_people_present}
    zone_types = get_zone_types()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT person_id, zone, timestamp FROM logs ORDER BY timestamp')
    logs = c.fetchall()
    conn.close()
    from collections import defaultdict
    zone_people = defaultdict(set)
    for person_id, zone, ts in logs:
        if zone_types.get(zone) == "meeting":
            zone_people[zone].add(person_id)
    # For each meeting zone, return number of unique people seen
    return {zone: len(people) for zone, people in zone_people.items()}

if __name__ == "__main__":
    # Example usage
    print("Productive hours:", calculate_productive_hours(1))
    print("Meeting hours:", calculate_meeting_hours(1))
    print("Break minutes:", calculate_break_times(1))
    print("Collaborative times:", calculate_collaborative_times())
