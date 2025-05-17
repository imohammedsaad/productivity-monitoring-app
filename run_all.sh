#!/bin/bash
# Run all main components of the productivity-monitoring-app

echo "Starting backend server..."
(cd backend && python app.py &)

echo "Starting video zone tool..."
(cd video_zone && python video_feed.py &)

echo "Starting detection and tracking..."
(cd detection_tracking && python detect.py &)

echo "Starting dashboard..."
(cd dashboard_supervisor && streamlit run dashboard.py &)

echo "All components started."
