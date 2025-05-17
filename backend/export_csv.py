import pandas as pd
from database import get_logs
import os

def export_logs_to_csv(csv_path='logs_export.csv'):
    logs = get_logs()
    df = pd.DataFrame([dict(row) for row in logs])
    df.to_csv(csv_path, index=False)
    print(f"Logs exported to {csv_path}")

if __name__ == "__main__":
    export_logs_to_csv()
