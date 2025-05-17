import streamlit as st
from api_client import get_alerts, get_contacts, get_stats, export_logs
from charts import plot_bar_chart, plot_line_chart
from heatmap import plot_heatmap

st.set_page_config(page_title="Productivity Dashboard", layout="wide")
st.title("Productivity Monitoring Dashboard")

# Sidebar: Person selection
contacts = get_contacts()
person_names = [c['name'] for c in contacts]
selected_person = st.sidebar.selectbox("Select Person", person_names)

# Real-time alerts
st.header("Real-time Alerts")
alerts = get_alerts()
for alert in alerts:
    st.warning(f"[{alert['timestamp']}] {alert['message']}")

# Per-person zone history (mock)
st.header(f"Zone History for {selected_person}")
st.write("(Zone history chart placeholder)")

# Click-to-call
person = next((c for c in contacts if c['name'] == selected_person), None)
if person:
    st.markdown(f"**Call:** [{person['phone']}](tel:{person['phone']})")

# Filter and deep view (mock)
st.header("Deep View")
st.write("(Detailed stats and logs for selected person)")

# Export logs
if st.button("Export Logs to CSV"):
    export_logs()
    st.success("Logs exported!")

# Heatmap
st.header("Live Occupancy Heatmap")
plot_heatmap()
