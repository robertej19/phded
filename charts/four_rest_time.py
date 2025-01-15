# charts/rest_time_hist.py

import numpy as np
import pandas as pd
import plotly.express as px

def create_rest_time_histogram(df: pd.DataFrame) -> px.histogram:
    """
    1) Computes a new column 'Rest Time' in hours, representing the time between
       consecutive lifts on consecutive days:
         Rest Time (day i) = 24 - (DecimalHour of day i-1) + (DecimalHour of day i)
       if day i is exactly day_number(previous) + 1.
    2) Returns a histogram of the 'Rest Time' distribution.

    Requirements:
      - The DataFrame has columns: "Day Number" (int) and "DecimalHour" (float).
      - The data must be sorted or can be sorted here to align consecutive days.
    """

    # Ensure needed columns exist
    required_cols = {"Day Number", "DecimalHour"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"DataFrame must contain {required_cols} columns.")

    # Sort by Day Number (and maybe DecimalHour if multiple lifts per day)
    df = df.sort_values(["Day Number", "DecimalHour"]).reset_index(drop=True)

    # Create a new column 'Rest Time' initialized to NaN
    df["Rest Time"] = np.nan

    # Iterate through rows to calculate consecutive rest times
    for i in range(1, len(df)):
        curr_day = df.loc[i, "Day Number"]
        prev_day = df.loc[i - 1, "Day Number"]

        curr_dec_hour = df.loc[i, "DecimalHour"]
        prev_dec_hour = df.loc[i - 1, "DecimalHour"]

        # If days are consecutive (e.g., day 10 => day 11)
        if curr_day == prev_day + 1:
            df.loc[i, "Rest Time"] = 24 - prev_dec_hour + curr_dec_hour

    # Build a histogram of 'Rest Time'
    # Drop any NaN since not all rows will have a rest time
    hist_df = df.dropna(subset=["Rest Time"])

    fig = px.histogram(
        hist_df,
        x="Rest Time",
        nbins=48,
        title="Histogram of Rest Time (hours)",
    )
    fig.update_layout(
        xaxis_title="Rest Time (hours)",
        yaxis_title="Count",
        template="plotly_white",
    )
    return fig
