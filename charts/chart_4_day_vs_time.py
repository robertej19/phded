import numpy as np
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt

def create_day_vs_time_of_day(df: pd.DataFrame) -> go.Figure:

    """
    Create a scatter plot of:
      - X-axis: Day number (derived from df["Date"])
      - Y-axis: Time of day in decimal hours [0=12AM .. 24=midnight]
      - Marker color: Weight lifted, with a Viridis colormap

    Assumes:
      - A "Date" column from which we calculate day-of-year.
      - A "Time" column in 'military time' float/string format (e.g., "1436.0").
      - A weight column named "Top Set Weight" or "Average Weight".
    """

    # --------- Helper function to parse 'Time' into decimal hours --------- #
    def to_decimal_hours(mil_time_str):
        """
        Converts military time (e.g., "1436.0" or "1436") to decimal hours (0..24).
        """
        if not isinstance(mil_time_str, str):
            mil_time_str = str(mil_time_str)
        mil_time_str = mil_time_str.replace(":", "")  # just in case
        
        try:
            t = int(float(mil_time_str))
            hh = t // 100
            mm = t % 100
            return hh + mm / 60.0
        except:
            return np.nan

    # --------- Ensure we have a valid weight column --------- #
    weight_col = "Top Set Weight" 
    if weight_col not in df.columns:
        weight_col = "Average Weight"
        if weight_col not in df.columns:
            raise ValueError(
                "No valid weight column found (expected 'Top Set Weight' or 'Average Weight')."
            )

    # --------- Ensure we can compute a day number from "Date" --------- #
    if "Date" not in df.columns:
        raise ValueError("DataFrame must have a 'Date' column to derive the day number.")
    
    # Convert "Date" column to datetime, then compute the day of year
    df["Date"] = pd.to_datetime(df["Date"])
    #df["DayNumber"] = df["Date"].dt.dayofyear  # or any other day calculation you want

    # --------- Convert 'Time' to decimal hours --------- #
    df["Time"] = df["Time"].astype(str)
    df["DecimalHour"] = df["Time"].apply(to_decimal_hours)

    # --------- Drop rows with invalid times or weights --------- #
    df = df.dropna(subset=["Day Number", "DecimalHour", weight_col])

    # --------- (Optional) define your own min/max for color scaling --------- #
    w_min = df[weight_col].min()
    w_max = df[weight_col].max()

    # --------- Build a hover template (optional) --------- #
    # We could show DayNumber, Time (HH:MM), Weight, etc.
    def decimal_hour_to_ampm(decimal_hour):
        """
        Convert decimal hour (e.g., 15.5) to a formatted AM/PM string (e.g., "3:30 PM").
        """
        hour = int(decimal_hour)
        minute = int(round((decimal_hour - hour) * 60))
        period = "AM" if hour < 12 else "PM"
        hour_12 = hour % 12
        hour_12 = 12 if hour_12 == 0 else hour_12
        return f"{hour_12}:{minute:02d} {period}"

    hover_text = [
        f"Day: {day}<br>Time: {decimal_hour_to_ampm(t)}<br>Weight: {wt} lbs"
        for day, t, wt in zip(df["Day Number"], df["DecimalHour"], df[weight_col])
    ]

    # --------- Create Plotly scatter figure --------- #
    fig = go.Figure(
        data=go.Scatter(
            x=df["Day Number"],
            y=df["DecimalHour"],
            mode="markers",
            marker=dict(
                size=5,
                color=df[weight_col],
                colorscale="Viridis",
                cmin=w_min,
                cmax=w_max,
                showscale=True,
                colorbar=dict(
                    title="Weight (lbs)",
                    title_font=dict(size=16),  # Increase colorbar title font
                    tickfont=dict(size=16)     # Increase colorbar tick font
                )
            ),
            text=hover_text,
            hovertemplate="%{text}<extra></extra>"
        )
    )

    # In the Scatter marker definition, set up colorbar with larger font size




    # --------- Set up axis ranges, labels, and layout --------- #
    fig.update_layout(
        autosize=True,
        font=dict(
            family="Arial, sans-serif",
            size=16,         # Global base font size
            color="#FFFFFF"
        ),
        title=dict(
            text="Day Number vs. Time of Day",
            font=dict(size=28, color="#FFFFFF")
        ),
        xaxis=dict(
            title=dict(
                text="Day Number",
                font=dict(size=20, color="#FFFFFF")
            ),
            tickfont=dict(size=16, color="#FFFFFF")
        ),
        yaxis=dict(
            title=dict(
                text="Time of Day",
                font=dict(size=20, color="#FFFFFF")
            ),
            tickmode="array",
            tickvals=[0, 4, 8, 12, 16, 20, 24],
            ticktext=["12 AM", "4 AM", "8 AM", "12 PM", "4 PM", "8 PM", "12 AM"],
            tickfont=dict(size=16, color="#FFFFFF"),
            range=[0, 24]
        ),
        template="plotly_dark",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)"
    )


    return fig

