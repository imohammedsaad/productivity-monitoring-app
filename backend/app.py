from flask import Flask, request, jsonify, send_file
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'productivity.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id INTEGER,
        zone TEXT,
        timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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

@app.route('/log', methods=['POST'])
def log_activity():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO logs (person_id, zone, timestamp) VALUES (?, ?, ?)',
              (data.get('id'), data.get('zone'), data.get('timestamp', datetime.now().isoformat())))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/stats')
def stats():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT zone, COUNT(*) as count FROM logs GROUP BY zone')
    stats = c.fetchall()
    conn.close()
    return jsonify([dict(row) for row in stats])

@app.route('/alerts')
def get_alerts():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 20')
    alerts = c.fetchall()
    conn.close()
    return jsonify([dict(row) for row in alerts])

@app.route('/contacts')
def get_contacts():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM contacts')
    contacts = c.fetchall()
    conn.close()
    return jsonify([dict(row) for row in contacts])

@app.route('/export')
def export_csv():
    import pandas as pd
    conn = get_db()
    df = pd.read_sql_query('SELECT * FROM logs', conn)
    csv_path = os.path.join(os.path.dirname(__file__), 'logs_export.csv')
    df.to_csv(csv_path, index=False)
    conn.close()
    return send_file(csv_path, as_attachment=True)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
