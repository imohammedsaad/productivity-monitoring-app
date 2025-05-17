import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'productivity.db')

# Example zone tags for demo
PRODUCTIVE_ZONES = ['Desk', 'Work Area']
BREAK_ZONES = ['Break Room', 'Lounge']
MEETING_ZONES = ['Meeting Room']

def get_logs_for_person(person_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT zone, timestamp FROM logs WHERE person_id=? ORDER BY timestamp', (person_id,))
    logs = c.fetchall()
    conn.close()
    return logs

def calculate_times(person_id):
    logs = get_logs_for_person(person_id)
    times = {'productive': 0, 'break': 0, 'meeting': 0}
    last_time = None
    last_zone = None
    for zone, ts in logs:
        t = datetime.fromisoformat(ts)
        if last_time and last_zone:
            delta = (t - last_time).total_seconds() / 60  # minutes
            if last_zone in PRODUCTIVE_ZONES:
                times['productive'] += delta
            elif last_zone in BREAK_ZONES:
                times['break'] += delta
            elif last_zone in MEETING_ZONES:
                times['meeting'] += delta
        last_time = t
        last_zone = zone
    return times

if __name__ == "__main__":
    print(calculate_times(1))
