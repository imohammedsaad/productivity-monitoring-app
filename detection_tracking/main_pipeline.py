import cv2
import torch
import requests
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from zone_mapper import load_zones, map_tracks_to_zones
from send_to_backend import send_logs_batch
from utils import format_frame
from datetime import datetime
import json
from reid_utils import load_reid_model, extract_reid_feature
import numpy as np
from flask import Flask, request, jsonify
from db_utils import get_db

app = Flask(__name__)

print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("CUDA device:", torch.cuda.get_device_name(0))

# Load YOLOv8 model and DeepSORT tracker
def load_model_and_tracker():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")  # This will confirm GPU usage
    model = YOLO('yolov8n.pt')
    model.to(device)
    tracker = DeepSort(max_age=15, n_init=1, nms_max_overlap=0.7)
    return model, device, tracker

def detect_people(frame, model, device):
    results = model(frame[..., ::-1], device=device)
    detections = []
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            if model.names[cls] == 'person':
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                detections.append({'bbox': [x1, y1, x2, y2], 'confidence': conf})
    return detections

# Fetch contacts mapping from backend
def fetch_contacts():
    try:
        resp = requests.get("http://localhost:5000/contacts")
        if resp.status_code == 200:
            # Build a dict: person_id -> name
            return {str(c['person_id']): c['name'] for c in resp.json()}
    except Exception as e:
        print("Could not fetch contacts:", e)
    return {}

@app.route('/log', methods=['POST'])
def log_activity():
    data = request.json
    person_id = data.get('person_id', data.get('id'))
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO logs (person_id, name, zone, zone_type, event, timestamp, duration_in_zone, anomaly)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (person_id, data['name'], data['zone'], data['zone_type'], data['event'],
               data['timestamp'], data['duration_in_zone'], data['anomaly']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

def send_logs_batch(logs):
    for log in logs:
        try:
            print(type(log))
            print(log)
            resp = requests.post("http://localhost:5000/log", json=log)
            print("Sent log:", log, "Response: ", "resp==>",resp,resp.json())
            break
        except Exception as e:
            print("Failed to send log:", e)

# Heatmap accumulator and decay factor
heatmap_accumulator = None
heatmap_decay = 0.95  # Decay factor for fading old heat

def main():
    global heatmap_accumulator

    model, device, tracker = load_model_and_tracker()
    reid_model = load_reid_model()
    gallery = {}  # person_id -> (feature, last_seen_frame)
    gallery_max_age = 100  # frames to keep old features

    zones = load_zones()
    zone_types = {z['name']: z['type'] for z in zones}
    contacts = fetch_contacts()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    frame_count = 0
    process_every_n = 6 # Process every 3rd frame
    last_frame_disp = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Initialize heatmap_accumulator after reading the first frame
        if heatmap_accumulator is None:
            heatmap_accumulator = np.zeros((frame.shape[0], frame.shape[1]), dtype=np.float32)

        if frame_count % 300 == 0:
            contacts = fetch_contacts()
        if frame_count % process_every_n == 0:
            detections = detect_people(frame, model, device)
            dets = []
            for det in detections:
                x1, y1, x2, y2 = det['bbox']
                conf = det['confidence']
                cls = 0  # 0 for 'person', since you only detect persons
                dets.append([[x1, y1, x2, y2], conf, cls])
            tracks_raw = tracker.update_tracks(dets, frame=frame)
            tracks = []
            for track in tracks_raw:
                if not track.is_confirmed():
                    continue
                track_id = track.track_id
                ltrb = track.to_ltrb()
                tracks.append({'id': track_id, 'bbox': list(map(int, ltrb))})
            # Re-identification logic
            for track in tracks:
                x1, y1, x2, y2 = track['bbox']
                crop = frame[y1:y2, x1:x2]
                if crop.size == 0:
                    continue
                feat = extract_reid_feature(reid_model, crop)

                # Try to match with gallery
                matched_id = None
                min_dist = float('inf')
                for pid, (gallery_feat, last_seen) in gallery.items():
                    dist = np.linalg.norm(feat - gallery_feat)
                    if dist < 0.6 and dist < min_dist:  # 0.6 is a typical threshold
                        matched_id = pid
                        min_dist = dist

                if matched_id is not None:
                    # Assign old ID to this track
                    track['id'] = matched_id
                else:
                    # New ID (keep DeepSORT's assignment)
                    matched_id = track['id']

                # Update gallery
                gallery[matched_id] = (feat, frame_count)

            # Remove old entries from gallery
            to_remove = [pid for pid, (_, last_seen) in gallery.items() if frame_count - last_seen > gallery_max_age]
            for pid in to_remove:
                del gallery[pid]

            mapped = map_tracks_to_zones(tracks, zones)
            logs = []
            now = datetime.now().isoformat()
            for mapped_track in mapped:
                print("*********************************************************************************")
                # Determine status
                zone_type = mapped_track.get('zone_type', 'active')
                status = 'active' if zone_type == 'active' else 'idle'
                # Add status to log
                log = {
                    #'id': mapped_track['id'],
                    'person_id': mapped_track['id'],
                    'name': contacts.get(str(mapped_track['id']), f"ID {mapped_track['id']}"),
                    'zone': mapped_track['zone'],
                    'zone_type': zone_type,
                    'event': 'entered' if mapped_track.get('event') == 'enter' else 'exited',
                    'timestamp': now,
                    'duration_in_zone': mapped_track.get('duration_in_zone', 0),  
                    'anomaly': mapped_track.get('anomaly', None),
                    'status': status
                }
                logs.append(log)
                # logs=log
                # Overlay status on video
                x1, y1, x2, y2 = mapped_track['bbox']
                cv2.putText(
                    frame_disp,
                    f"Status: {status.capitalize()}",
                    (x1, y2 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0) if status == 'active' else (0, 255, 255),
                    2
                )

            if logs:
                print("Sending logs:", logs)
                send_logs_batch(logs)
                for log in logs:
                    print("Logged:", json.dumps(log, indent=2))
            frame_disp = format_frame(frame, tracks)
            for track in tracks_raw:
                track_id = str(track.track_id)
                name = contacts.get(track_id, f"ID {track_id}")
                x1, y1, x2, y2 = track.to_ltrb()
                cv2.putText(frame_disp, name, (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            last_frame_disp = frame_disp.copy()

            # Update heatmap accumulator with tracks
            for track in tracks:
                x1, y1, x2, y2 = track['bbox']
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                # Add heat at the center of the bounding box
                cv2.circle(heatmap_accumulator, (cx, cy), 20, 1, -1)  # 20 is radius, 1 is intensity

            # Apply decay to fade old heat
            heatmap_accumulator *= heatmap_decay

            # Normalize and convert to color for overlay
            heatmap_norm = np.clip(heatmap_accumulator / heatmap_accumulator.max(), 0, 1) if heatmap_accumulator.max() > 0 else heatmap_accumulator
            heatmap_color = cv2.applyColorMap((heatmap_norm * 255).astype(np.uint8), cv2.COLORMAP_JET)

            # Overlay heatmap on frame
            overlay = cv2.addWeighted(frame_disp, 0.7, heatmap_color, 0.3, 0)

            # Show overlay instead of frame_disp
            cv2.imshow("Live Heatmap", overlay)
        else:
            if last_frame_disp is not None:
                cv2.imshow('Detection + Tracking + Zones', last_frame_disp)
            else:
                cv2.imshow('Detection + Tracking + Zones', frame)
        frame_count += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()