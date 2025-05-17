import numpy as np
import cv2

def iou(boxA, boxB):
    # Compute Intersection over Union between two boxes
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    iou = interArea / float(boxAArea + boxBArea - interArea + 1e-6)
    return iou

def centroid(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) // 2, (y1 + y2) // 2)

def format_frame(frame, tracks):
    # Draw bounding boxes, centroids, and IDs for tracked people
    for track in tracks:
        x1, y1, x2, y2 = track['bbox']
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
        cx, cy = centroid(track['bbox'])
        cv2.circle(frame, (cx, cy), 5, (255,0,0), -1)
        cv2.putText(frame, f"ID {track['id']}", (x1, y2+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    return frame

if __name__ == "__main__":
    # Test IoU and centroid
    boxA = [10, 10, 50, 50]
    boxB = [30, 30, 70, 70]
    print("IoU:", iou(boxA, boxB))
    print("Centroid A:", centroid(boxA))
    print("Centroid B:", centroid(boxB))
