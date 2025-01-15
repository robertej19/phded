import pandas as pd
import os, time

LOCAL_CSV = "local_data.csv"
ONE_DAY_IN_SECONDS = 86400

def is_data_stale(file_path):
    """Return True if file doesn't exist or is older than a day."""
    if not os.path.exists(file_path):
        return True
    file_age = time.time() - os.path.getmtime(file_path)
    return file_age > ONE_DAY_IN_SECONDS

def load_data(csv_url: str) -> pd.DataFrame:
    """
    1) Check if local CSV is stale.
    2) If stale or missing, fetch from the given csv_url and save locally.
    3) Return the DataFrame.
    """
    if is_data_stale(LOCAL_CSV):
        df = pd.read_csv(csv_url)
        df.to_csv(LOCAL_CSV, index=False)
    else:
        df = pd.read_csv(LOCAL_CSV)
    return df
