import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import requests
import pandas as pd

BACKEND_URL = "http://localhost:5000"  # Adjust if your backend runs elsewhere

def fetch_logs():
    try:
        resp = requests.get(f"{BACKEND_URL}/logs")
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error("Failed to fetch logs from backend.")
            return []
    except Exception as e:
        st.error(f"Error fetching logs: {e}")
        return []

def plot_heatmap():
    logs = fetch_logs()
    if not logs:
        st.warning("No log data available for heatmap.")
        return

    # Assume zones are labeled as "Zone 1", "Zone 2", etc.
    zones = sorted(list(set(log['zone'] for log in logs)))
    zone_to_idx = {zone: idx for idx, zone in enumerate(zones)}

    # Count presence per zone
    heatmap_data = np.zeros((1, len(zones)))
    for log in logs:
        idx = zone_to_idx.get(log['zone'])
        if idx is not None:
            heatmap_data[0, idx] += 1

    # Plot heatmap
    fig, ax = plt.subplots(figsize=(len(zones), 2))
    cax = ax.imshow(heatmap_data, cmap='hot', aspect='auto')
    ax.set_xticks(np.arange(len(zones)))
    ax.set_xticklabels(zones, rotation=45, ha='right')
    ax.set_yticks([])
    fig.colorbar(cax, orientation='vertical')
    ax.set_title("Zone Occupancy Heatmap (Real-Time)")
    st.pyplot(fig)

if __name__ == "__main__":
    plot_heatmap()
