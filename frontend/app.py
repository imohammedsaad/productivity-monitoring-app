from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

API_BASE = "http://localhost:5000"

def safe_get_json(url, default):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return default

@app.route("/", methods=["GET"])
def dashboard():
    logs = safe_get_json(f"{API_BASE}/log", [])
    stats = safe_get_json(f"{API_BASE}/stats", [])
    alerts = safe_get_json(f"{API_BASE}/alerts", [])
    contacts = safe_get_json(f"{API_BASE}/contacts", [])
    collaborative_times = safe_get_json(f"{API_BASE}/collaborative_times", [])
    statuses = safe_get_json(f"{API_BASE}/status", [])
    person_id = request.args.get("person_id")
    productive_hours = None
    meeting_hours = None
    break_times = None
    map_success = request.args.get("map_success")
    map_error = request.args.get("map_error")
    if person_id:
        productive_hours = safe_get_json(f"{API_BASE}/productive_hours/{person_id}", {"productive_hours": 0})
        meeting_hours = safe_get_json(f"{API_BASE}/meeting_hours/{person_id}", {"meeting_hours": 0})
        break_times = safe_get_json(f"{API_BASE}/break_times/{person_id}", {"break_minutes": 0})
    return render_template(
        "dashboard.html",
        logs=logs,
        stats=stats,
        alerts=alerts,
        contacts=contacts,
        collaborative_times=collaborative_times,
        statuses=statuses,
        productive_hours=productive_hours,
        meeting_hours=meeting_hours,
        break_times=break_times,
        person_id=person_id,
        map_success=map_success,
        map_error=map_error
    )

@app.route("/map_person", methods=["POST"])
def map_person():
    person_id = request.form.get("person_id")
    name = request.form.get("name")
    phone = request.form.get("phone")
    try:
        resp = requests.post(f"{API_BASE}/contacts", json={
            "person_id": person_id,
            "name": name,
            "phone": phone
        })
        if resp.status_code == 200:
            return redirect(url_for("dashboard", map_success=1))
        else:
            return redirect(url_for("dashboard", map_error=1))
    except Exception:
        return redirect(url_for("dashboard", map_error=1))

if __name__ == "__main__":
    app.run(port=8000, debug=True)