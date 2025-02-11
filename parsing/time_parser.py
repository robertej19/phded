import os
import subprocess
import json
from datetime import datetime, timedelta
import pandas as pd

# ------------------------------
# 1. Process all mp4 files in a folder
# ------------------------------

# Specify the directory containing your mp4 files
#directory = 'path/to/your/mp4_files'
directory = '/mnt/d/PHDED/0_Unsorted_Videos/2023'

# List to hold individual video records
records = []

for filename in os.listdir(directory):
    if filename.lower().endswith('.mp4'):
        filepath = os.path.join(directory, filename)
        
        # Use ffprobe to get metadata (both format and streams)
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            filepath
        ]
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            metadata = json.loads(result.stdout)
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue
        
        # Attempt to get the creation time from metadata
        creation_time_str = None
        if "format" in metadata and "tags" in metadata["format"]:
            creation_time_str = metadata["format"]["tags"].get("creation_time")
        
        # If not available, use the file's modification time
        if creation_time_str is None:
            mtime = os.path.getmtime(filepath)
            creation_time_str = datetime.fromtimestamp(mtime).isoformat()
        
        # Parse the creation time string into a datetime object.
        # Replace "Z" with "+00:00" to ensure proper parsing.
        try:
            dt = datetime.fromisoformat(creation_time_str.replace("Z", "+00:00"))
        except Exception as e:
            print(f"Error parsing date for {filename}: {e}")
            continue
        
        # ------------------------------
        # 1. Adjust the time by subtracting 5 hours
        # ------------------------------
        dt = dt - timedelta(hours=5)
        
        # Format date as YYYYMMDD and time as HHMM (no colon)
        date_str = dt.strftime("%Y%m%d")
        time_str = dt.strftime("%H%M")
        
        # ------------------------------
        # 2. Determine the video type
        # ------------------------------
        # If any video stream has a width or height of 3840, classify as "DJI"; otherwise, "Phone"
        video_type = "Phone"  # default
        if "streams" in metadata:
            for stream in metadata["streams"]:
                if stream.get("codec_type") == "video":
                    width = stream.get("width")
                    height = stream.get("height")
                    if width == 3840 or height == 3840:
                        video_type = "DJI"
                        break
        
        # Save the record (one per video)
        records.append({
            "date": date_str,
            "time": time_str,
            "type": video_type
        })

# Convert the list of records to a DataFrame
df = pd.DataFrame(records)

# ------------------------------
# 2. Aggregate by date so that each date appears only once.
#    If there is only one video on a date, use its time and type.
#    If there are multiple videos on the same date, set time to empty.
# ------------------------------
aggregated = []
for date, group in df.groupby("date"):
    if len(group) == 1:
        rec_time = group.iloc[0]["time"]
        rec_type = group.iloc[0]["type"]
    else:
        # For duplicate dates, leave time blank.
        rec_time = ""
        # Optionally: if all videos for that date share the same type, you might keep it.
        types = group["type"].unique()
        rec_type = types[0] if len(types) == 1 else ""
    aggregated.append({
        "date": date,
        "time": rec_time,
        "type": rec_type
    })

agg_df = pd.DataFrame(aggregated)

# ------------------------------
# 3. Insert missing dates between the min and max dates
# ------------------------------
if not agg_df.empty:
    # Convert the 'date' column to datetime objects for comparison
    agg_df["date_dt"] = pd.to_datetime(agg_df["date"], format="%Y%m%d")
    min_date = agg_df["date_dt"].min()
    max_date = agg_df["date_dt"].max()
    
    # Create a complete date range from min_date to max_date
    all_dates = pd.date_range(min_date, max_date, freq='D')
    all_dates_str = all_dates.strftime("%Y%m%d")
    
    # Create a DataFrame for all dates with empty time and type values
    all_dates_df = pd.DataFrame({"date": all_dates_str})
    all_dates_df["time"] = ""
    all_dates_df["type"] = ""
    
    # Merge the aggregated video data with the complete date list.
    # If a date from all_dates_df is missing in agg_df, its time and type remain empty.
    final_df = pd.merge(all_dates_df, agg_df.drop(columns=["date_dt"]), on="date", how="left", suffixes=("", "_agg"))
    
    # For dates present in agg_df, use its time and type; otherwise, keep the empty strings.
    final_df["time"] = final_df["time_agg"].combine_first(final_df["time"])
    final_df["type"] = final_df["type_agg"].combine_first(final_df["type"])
    final_df.drop(columns=["time_agg", "type_agg"], inplace=True)
    
    # Ensure the final DataFrame is sorted by date
    final_df = final_df.sort_values("date").reset_index(drop=True)
else:
    final_df = agg_df

# ------------------------------
# Save the final DataFrame as a CSV
# ------------------------------
output_csv = "output.csv"
final_df.to_csv(output_csv, index=False)
print(f"CSV saved to {output_csv}")