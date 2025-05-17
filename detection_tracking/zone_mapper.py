import json
import os

def load_zones(zones_path=None):
    if zones_path is None:
        zones_path = os.path.join(os.path.dirname(__file__), '../video_zone/zones.json')
    with open(zones_path, 'r') as f:
        return json.load(f)

def is_in_zone(bbox, zone):
    x1, y1, x2, y2 = bbox
    zx1, zy1, zx2, zy2 = zone['x1'], zone['y1'], zone['x2'], zone['y2']
    # Check if bbox center is inside zone
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    return zx1 <= cx <= zx2 and zy1 <= cy <= zy2

def map_tracks_to_zones(tracks, zones):
    # tracks: list of dicts with 'id' and 'bbox'
    results = []
    for track in tracks:
        for zone in zones:
            if is_in_zone(track['bbox'], zone):
                results.append({'id': track['id'], 'zone': zone['label']})
    return results

if __name__ == "__main__":
    zones = load_zones()
    tracks = [
        {'id': 1, 'bbox': [253, 149, 439, 329]},
        {'id': 2, 'bbox': [52, 54, 141, 250]}
    ]
    print(map_tracks_to_zones(tracks, zones))
