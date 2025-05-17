import cv2
import torch
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from zone_mapper import load_zones, map_tracks_to_zones
from send_to_backend import send_logs_batch
from utils import format_frame
from datetime import datetime

# Load YOLOv8 model and DeepSORT tracker
def load_model_and_tracker():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = YOLO('yolov8n.pt')
    model.to(device)
    tracker = DeepSort(max_age=30, n_init=3, nms_max_overlap=1.0)
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

def main():
    model, device, tracker = load_model_and_tracker()
    zones = load_zones()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        detections = detect_people(frame, model, device)
        dets = [[*det['bbox'], det['confidence']] for det in detections]
        tracks_raw = tracker.update_tracks(dets, frame=frame)
        # Prepare tracks for zone mapping and display
        tracks = []
        for track in tracks_raw:
            if not track.is_confirmed():
                continue
            track_id = track.track_id
            ltrb = track.to_ltrb()
            tracks.append({'id': track_id, 'bbox': list(map(int, ltrb))})
        # Map tracks to zones
        mapped = map_tracks_to_zones(tracks, zones)
        # Prepare logs for backend
        logs = []
        now = datetime.now().isoformat()
        for m in mapped:
            logs.append({'id': m['id'], 'zone': m['zone'], 'timestamp': now})
        if logs:
            send_logs_batch(logs)
        # Draw everything
        frame_disp = format_frame(frame, tracks)
        cv2.imshow('Detection + Tracking + Zones', frame_disp)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 