import sqlite3
import os

def get_db(db_path=None):
    if db_path is None:
        db_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'productivity.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn