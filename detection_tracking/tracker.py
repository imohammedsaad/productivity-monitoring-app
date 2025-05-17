import cv2
import torch
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

def load_model():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = YOLO('yolov8n.pt')
    model.to(device)
    return model, device

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
    model, device = load_model()
    tracker = DeepSort(max_age=30, n_init=3, nms_max_overlap=1.0)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        detections = detect_people(frame, model, device)
        # DeepSORT expects: [[x1, y1, x2, y2, confidence], ...]
        dets = [[*det['bbox'], det['confidence']] for det in detections]
        tracks = tracker.update_tracks(dets, frame=frame)
        for track in tracks:
            if not track.is_confirmed():
                continue
            track_id = track.track_id
            ltrb = track.to_ltrb()
            x1, y1, x2, y2 = map(int, ltrb)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255,0,0), 2)
            cv2.putText(frame, f"ID {track_id}", (x1, y2+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)
        cv2.imshow('Tracking', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
