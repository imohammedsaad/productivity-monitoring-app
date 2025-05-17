import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'productivity.db')

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def add_log(person_id, zone, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    conn = connect()
    c = conn.cursor()
    c.execute('INSERT INTO logs (person_id, zone, timestamp) VALUES (?, ?, ?)', (person_id, zone, timestamp))
    conn.commit()
    conn.close()

def add_contact(name, phone):
    conn = connect()
    c = conn.cursor()
    c.execute('INSERT INTO contacts (name, phone) VALUES (?, ?)', (name, phone))
    conn.commit()
    conn.close()

def add_alert(alert_type, message, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    conn = connect()
    c = conn.cursor()
    c.execute('INSERT INTO alerts (type, message, timestamp) VALUES (?, ?, ?)', (alert_type, message, timestamp))
    conn.commit()
    conn.close()

def get_logs():
    conn = connect()
    c = conn.cursor()
    c.execute('SELECT * FROM logs')
    logs = c.fetchall()
    conn.close()
    return logs

def get_contacts():
    conn = connect()
    c = conn.cursor()
    c.execute('SELECT * FROM contacts')
    contacts = c.fetchall()
    conn.close()
    return contacts

def get_alerts():
    conn = connect()
    c = conn.cursor()
    c.execute('SELECT * FROM alerts')
    alerts = c.fetchall()
    conn.close()
    return alerts

if __name__ == "__main__":
    add_contact('Alice', '+123456789')
    add_alert('idle', 'Person 1 idle for 10 min')
    add_log(1, 'Zone 1')
    print(list(get_contacts()))
    print(list(get_alerts()))
    print(list(get_logs()))
