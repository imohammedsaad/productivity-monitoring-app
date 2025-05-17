# Productivity Monitoring App

A modular system for real-time productivity monitoring in shared workspaces. It uses video feeds to detect and track people, maps them to defined zones (desks, rooms, break areas), logs activity to a backend, and provides a real-time dashboard for supervisors.

## Project Structure

- `video_zone/`: Define and save zones on video feeds (OpenCV)
- `detection_tracking/`: Detect and track people in video frames (YOLOv8 + DeepSORT/ByteTrack)
- `backend/`: Flask API server, SQLite DB, business logic
- `dashboard_supervisor/`: Streamlit dashboard for real-time monitoring and analytics
- `shared/`: Shared utilities and constants

## Prerequisites
- Python 3.8+
- pip (Python package manager)
- (Optional) OpenCV, PyTorch, Streamlit, Flask, SQLite3

## Installation
```bash
pip install -r requirements.txt
```

## Running the App
1. **Start the backend server:**
    ```bash
    cd backend
    python app.py
    ```
2. **Run the video zone tool:**
    ```bash
    cd video_zone
    python video_feed.py
    # or python zone_drawer.py
    ```
3. **Run detection and tracking:**
    ```bash
    cd detection_tracking
    python detect.py
    # or python tracker.py
    ```
4. **Start the dashboard:**
    ```bash
    cd dashboard_supervisor
    streamlit run dashboard.py
    ```

## Workflow
1. Define zones on the video feed and save them.
2. Detect and track people in real-time, map them to zones.
3. Log activity to the backend server.
4. View real-time alerts, analytics, and heatmaps on the dashboard.

## Authors
- Member A: Zone definition, video feed
- Member B: Detection, tracking
- Member C: Backend, DB, API
- Member D: Dashboard, analytics

---
For more details, see comments in each file.
