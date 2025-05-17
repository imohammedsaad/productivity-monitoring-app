import cv2
import torch
from ultralytics import YOLO

# Load YOLOv8 model (person detection)
def load_model():
    # Use GPU if available
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = YOLO('yolov8n.pt')  # Use nano model for speed; change as needed
    model.to(device)
    return model, device

def detect_people(frame, model, device):
    # YOLO expects RGB
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
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        detections = detect_people(frame, model, device)
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,0,255), 2)
            cv2.putText(frame, f"Person {det['confidence']:.2f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
        cv2.imshow('Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
