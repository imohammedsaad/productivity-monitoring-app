import cv2
import json

ZONES_FILE = 'zones.json'

drawing = False
ix, iy = -1, -1
zones = []
current_rect = None

def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, current_rect
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        current_rect = (ix, iy, x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        current_rect = (ix, iy, x, y)
        zones.append({'x1': ix, 'y1': iy, 'x2': x, 'y2': y, 'label': f'Zone {len(zones)+1}'})
        current_rect = None

def main():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not grab frame.")
        return
    clone = frame.copy()
    cv2.namedWindow('Draw Zones')
    cv2.setMouseCallback('Draw Zones', draw_rectangle)
    while True:
        display = clone.copy()
        for z in zones:
            cv2.rectangle(display, (z['x1'], z['y1']), (z['x2'], z['y2']), (0,255,0), 2)
            cv2.putText(display, z['label'], (z['x1'], z['y1']-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
        if current_rect:
            x1, y1, x2, y2 = current_rect
            cv2.rectangle(display, (x1, y1), (x2, y2), (255,0,0), 1)
        cv2.imshow('Draw Zones', display)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            with open(ZONES_FILE, 'w') as f:
                json.dump(zones, f, indent=2)
            print(f"Zones saved to {ZONES_FILE}")
        elif key == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
