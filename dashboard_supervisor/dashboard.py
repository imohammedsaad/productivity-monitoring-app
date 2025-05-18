import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from api_client import get_alerts, get_contacts, get_stats, export_logs
from streamlit_autorefresh import st_autorefresh
st.set_page_config(page_title="Productivity Dashboard", layout="wide")

# Add this line to auto-refresh every 5 seconds (5000 ms)
st_autorefresh(interval=5000, key="zone_occupancy_autorefresh")

BACKEND_URL = "http://localhost:5000"

st.title("Productivity Monitoring Dashboard")

# --- Sidebar: Person selection ---
contacts = get_contacts()
person_names = [c['name'] for c in contacts]
selected_person = st.sidebar.selectbox("Select Person", person_names)
person = next((c for c in contacts if c['name'] == selected_person), None)
person_id = person['person_id'] if person else None

# --- Live Alerts Panel ---
st.header("🔔 Real-time Alerts")
alerts = get_alerts()
if alerts:
    for alert in alerts[:10]:
        st.warning(f"[{alert['timestamp']}] {alert['type'].upper()}: {alert['message']}")
else:
    st.success("No alerts at the moment.")

# --- Zone Occupancy Bar Chart ---
st.header("🏢 Zone Occupancy")
stats = get_stats()
if stats:
    df_stats = pd.DataFrame(stats)
    st.bar_chart(df_stats.set_index('zone')['count'])
else:
    st.info("No zone stats available.")

# --- Per-person Productivity/Meeting/Break Stats ---
st.header(f"👤 Productivity Stats for {selected_person}")
if person_id:
    prod = requests.get(f"{BACKEND_URL}/productive_hours/{person_id}").json()
    meet = requests.get(f"{BACKEND_URL}/meeting_hours/{person_id}").json()
    brk = requests.get(f"{BACKEND_URL}/break_times/{person_id}").json()
    st.metric("Productive Hours", f"{prod['productive_hours']:.2f}")
    st.metric("Meeting Hours", f"{meet['meeting_hours']:.2f}")
    st.metric("Break Minutes", f"{brk['break_minutes']:.2f}")

    # Pie chart
    pie_data = [prod['productive_hours'], meet['meeting_hours'], brk['break_minutes']/60]
    pie_labels = ['Productive', 'Meeting', 'Break']

    if sum(pie_data) > 0 and not any(pd.isna(x) for x in pie_data):
        fig, ax = plt.subplots()
        ax.pie(pie_data, labels=pie_labels, autopct='%1.1f%%', colors=['#4CAF50','#2196F3','#FFC107'])
        ax.axis('equal')
        st.pyplot(fig)
    else:
        st.info("No productivity data available to display pie chart.")

# --- Collaborative Times ---
st.header("🤝 Collaborative Usage (Meeting Rooms)")
collab = requests.get(f"{BACKEND_URL}/collaborative_times").json()
if collab:
    df_collab = pd.DataFrame(list(collab.items()), columns=['Meeting Room', 'Unique People'])
    st.table(df_collab)
else:
    st.info("No collaborative data available.")

# --- Heatmap ---
st.header("🔥 Live Occupancy Heatmap")
def fetch_logs():
    resp = requests.get(f"{BACKEND_URL}/logs")
    return resp.json() if resp.status_code == 200 else []

logs = fetch_logs()
if logs:
    zones = sorted(list(set(log['zone'] for log in logs)))
    zone_to_idx = {zone: idx for idx, zone in enumerate(zones)}
    heatmap_data = np.zeros((1, len(zones)))
    for log in logs:
        idx = zone_to_idx.get(log['zone'])
        if idx is not None:
            heatmap_data[0, idx] += 1
    fig, ax = plt.subplots(figsize=(len(zones), 2))
    cax = ax.imshow(heatmap_data, cmap='hot', aspect='auto')
    ax.set_xticks(np.arange(len(zones)))
    ax.set_xticklabels(zones, rotation=45, ha='right')
    ax.set_yticks([])
    fig.colorbar(cax, orientation='vertical')
    st.pyplot(fig)
else:
    st.info("No log data available for heatmap.")

# --- Export logs ---
st.header("⬇️ Export Logs")
if st.button("Export Logs to CSV"):
    export_logs()
    st.success("Logs exported to logs_export.csv!")

# --- Person ID Mapping (Admin) ---
st.header("🛠️ Person ID Mapping Setup")
with st.form("person_id_mapping"):
    person_id_input = st.text_input("Person ID")
    name_input = st.text_input("Name")
    phone_input = st.text_input("Phone Number")
    submitted = st.form_submit_button("Save Mapping")
    if submitted:
        resp = requests.post(f"{BACKEND_URL}/contacts", json={
            "person_id": person_id_input,
            "name": name_input,
            "phone": phone_input
        })
        if resp.status_code == 200:
            st.success("Mapping saved!")
        else:
            st.error("Failed to save mapping.")

# --- Current Zone for Each Person ---
contacts = requests.get(f"{BACKEND_URL}/contacts").json()
logs = requests.get(f"{BACKEND_URL}/logs").json()

# Build a DataFrame for logs
df_logs = pd.DataFrame(logs)
# Get the latest log for each person
if not df_logs.empty:
    df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp'])
    latest_logs = df_logs.sort_values('timestamp').groupby('id').tail(1)
    # Merge with contacts for names
    df_contacts = pd.DataFrame(contacts)
    merged = latest_logs.merge(df_contacts, left_on='id', right_on='person_id', how='left')
    merged = merged[['id', 'name', 'zone', 'timestamp']]
    merged = merged.rename(columns={'id': 'Person ID', 'name': 'Name', 'zone': 'Current Zone', 'timestamp': 'Last Seen'})
    st.header("🧑‍💼 Current Zone for Each Person")
    st.table(merged)
else:
    st.info("No logs available to determine current zones.")