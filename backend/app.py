from flask import Flask, request, jsonify, send_file
import sqlite3
import os
from datetime import datetime
import csv
from time_tracker import (
    calculate_productive_hours,
    calculate_meeting_hours,
    calculate_break_times,
    calculate_collaborative_times
)

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), '../backend/productivity.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id TEXT DEFAULT '0',
        name TEXT DEFAULT 'User',  
        zone TEXT  DEFAULT 'meeting',
        zone_type TEXT default 'desk',
        event TEXT DEFAULT 'entered',
        timestamp TEXT,
        duration_in_zone INTEGER DEFAULT 10,
        anomaly TEXT DEFAULT 'NULL',
        status TEXT DEFAULT 'active'
    )''')
    c.execute('DROP TABLE IF EXISTS contacts')
    c.execute('''CREATE TABLE IF NOT EXISTS contacts (
        person_id TEXT PRIMARY KEY,
        name TEXT,
        phone TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        message TEXT,
        timestamp TEXT
    )''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "message": "Productivity Monitoring API is running.",
        "available_endpoints": [
            "/logs",
            "/stats",
            "/alerts",
            "/contacts",
            "/log",
            "/export",
            "/productive_hours/<person_id>",
            "/meeting_hours/<person_id>",
            "/break_times/<person_id>",
            "/collaborative_times",
            "/status"
        ]
    })

@app.route('/logs', methods=['GET'])
def get_logs():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM logs')
    logs = c.fetchall()
    conn.close()
    return jsonify([dict(row) for row in logs])

@app.route('/stats', methods=['GET'])
def get_stats():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT zone, COUNT(DISTINCT person_id) as count FROM logs GROUP BY zone')
    stats = [{'zone': row['zone'], 'count': row['count']} for row in c.fetchall()]
    conn.close()
    return jsonify(stats)

@app.route('/alerts', methods=['GET'])
def get_alerts_api():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 20')
    alerts = c.fetchall()
    conn.close()
    return jsonify([dict(row) for row in alerts])

@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    conn = get_db()
    c = conn.cursor()
    if request.method == 'POST':
        data = request.json
        c.execute('INSERT OR REPLACE INTO contacts (person_id, name, phone) VALUES (?, ?, ?)',
                  (data['person_id'], data['name'], data.get('phone', '')))
        conn.commit()
        conn.close()
        return jsonify({'status': 'ok'})
    else:
        c.execute('SELECT * FROM contacts')
        contacts = c.fetchall()
        conn.close()
        return jsonify([dict(row) for row in contacts])

@app.route('/log', methods=['POST'])
def log_activity():
    data = request.json
    print("Received log:", data)  # Debug print
    person_id = data.get('person_id', data.get('id'))
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO logs (person_id, name, zone, zone_type, event, timestamp, duration_in_zone, anomaly, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (person_id, data.get('name'), data.get('zone'), data.get('zone_type'), data.get('event'),
               data.get('timestamp'), data.get('duration_in_zone'), data.get('anomaly'), data.get('status', 'active')))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/export', methods=['GET'])
def export_logs():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM logs')
    logs = c.fetchall()
    csv_path = os.path.join(os.path.dirname(__file__), 'logs_export.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=logs[0].keys())
        writer.writeheader()
        for row in logs:
            writer.writerow(dict(row))
    conn.close()
    return send_file(csv_path, as_attachment=True)

@app.route('/productive_hours/<person_id>', methods=['GET'])
def productive_hours(person_id):
    hours = calculate_productive_hours(person_id)
    return jsonify({'person_id': person_id, 'productive_hours': hours})

@app.route('/meeting_hours/<person_id>', methods=['GET'])
def meeting_hours(person_id):
    hours = calculate_meeting_hours(person_id)
    return jsonify({'person_id': person_id, 'meeting_hours': hours})

@app.route('/break_times/<person_id>', methods=['GET'])
def break_times(person_id):
    minutes = calculate_break_times(person_id)
    return jsonify({'person_id': person_id, 'break_minutes': minutes})

@app.route('/collaborative_times', methods=['GET'])
def collaborative_times():
    times = calculate_collaborative_times()
    return jsonify(times)

@app.route('/status', methods=['GET'])
def get_status():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT person_id, name, zone, zone_type, status, MAX(timestamp) as last_seen
        FROM logs
        GROUP BY person_id
    ''')
    statuses = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(statuses)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
