# Shared constants for backend and other modules

ZONE_TAGS = ['Desk', 'Work Area', 'Break Room', 'Lounge', 'Meeting Room', 'Restricted']
ZONE_THRESHOLDS = {
    'Desk': 1,
    'Work Area': 5,
    'Break Room': 3,
    'Meeting Room': 8,
    'Restricted': 0
}
SHARED_VALUES = {
    'idle_time_threshold': 10,  # minutes
    'overcapacity_alert': True
}
