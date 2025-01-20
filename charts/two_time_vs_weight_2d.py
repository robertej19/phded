import numpy as np
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt

def create_time_vs_weight_2d(df: pd.DataFrame) -> go.Figure:
    """
    Create a 2D histogram of 'Time' (horizontal axis) vs. 'Weight' (vertical axis),
    in 10 lb increments from min to max weight.
    
    Assumes:
      - The DataFrame has a 'Time' column in military float (e.g., 1436.0).
      - The DataFrame has been converted to decimal hours in a column named 'DecimalHour'.
      - A weight column (e.g., 'Top Set Weight' or 'Average Weight') is present.
    """
    def to_decimal_hours(mil_time_str):
        # Remove any ':' just in case
        mil_time_str = mil_time_str.replace(":", "")
        try:
            # Convert to float to handle "1436.0", then to int
            t = int(float(mil_time_str))  
            hh = t // 100
            mm = t % 100
            return hh + mm / 60.0
        except:
            return np.nan

    # 1) Determine which weight column to use
    #    Customize as needed, e.g. "Top Set Weight" or "Average Weight"
    weight_col = "Top Set Weight" 
    if weight_col not in df.columns:
        # Fallback to "Average Weight" if "Top Set Weight" not found
        weight_col = "Average Weight"
        if weight_col not in df.columns:
            raise ValueError("No valid weight column found (e.g., 'Top Set Weight' or 'Average Weight').")

    # Ensure "Time" is string, then parse
    df["Time"] = df["Time"].astype(str)
    print(df["Time"])

    df["DecimalHour"] = df["Time"].apply(to_decimal_hours)

    # 2) Drop rows with invalid time or weight
    df = df.dropna(subset=["DecimalHour", weight_col])

    # 3) Prepare bin edges
    #    Time bins: 1.0 hour increments from 0..24
    time_min, time_max = 0, 24
    time_bin_width = 1.0
    time_bins = np.arange(time_min, time_max + time_bin_width, time_bin_width)

    #    Weight bins: 10 lb increments from min to max
    w_min = df[weight_col].min()
    w_max = df[weight_col].max()
    w_min_10 = 10 * np.floor(w_min / 10)  # Round down to nearest 10
    w_max_10 = 10 * np.ceil(w_max / 10)   # Round up to nearest 10
    weight_bins = np.arange(w_min_10, w_max_10 + 10, 10)

    # 4) Calculate 2D histogram
    H, xedges, yedges = np.histogram2d(
        x=df["DecimalHour"],
        y=df[weight_col],
        bins=[time_bins, weight_bins]
    )

    # Set zeros to NaN for "bad" values
    H = np.where(H == 0, np.nan, H)

    # 5) Define bin centers for Plotly heatmap
    xcenters = 0.5 * (xedges[:-1] + xedges[1:])
    ycenters = 0.5 * (yedges[:-1] + yedges[1:])

    # 6) Use matplotlib colormap with set_bad("white")
    viridis = plt.cm.viridis.copy()
    viridis.set_bad("white")  # Set NaN (bad) values to white
    # Convert matplotlib colormap to Plotly colorscale
    plotly_colorscale = [
        [i / 255.0, f"rgb({r},{g},{b})"]
        for i, (r, g, b, _) in enumerate((viridis(np.linspace(0, 1, 256)) * 255).astype(int))
    ]

    # 7) Format time bins in AM/PM format
    def decimal_hour_to_ampm(decimal_hour):
        """
        Convert a decimal hour (e.g., 15.5) to a formatted AM/PM string (e.g., "3:30 PM").
        """
        hour = int(decimal_hour)
        minute = int(round((decimal_hour - hour) * 60))
        period = "AM" if hour < 12 else "PM"
        hour = hour % 12
        hour = 12 if hour == 0 else hour
        return f"{hour}:{minute:02d} {period}"

    #time_labels = [decimal_hour_to_ampm(x) for x in xcenters]
    #Only include every third time label
    time_labels = [decimal_hour_to_ampm(x) if i % 3 == 0 else "" for i, x in enumerate(xcenters)]

    # 8) Create hover text as 2D array
    hover_text = np.full(H.shape, "", dtype=object)

    for i in range(len(xcenters)):  # time bins
        for j in range(len(ycenters)):  # weight bins
            count = H[i, j]
            if not np.isnan(count):
                time_range = f"{decimal_hour_to_ampm(xedges[i])} - {decimal_hour_to_ampm(xedges[i + 1])}"
                weight_range = f"{int(yedges[j])} - {int(yedges[j + 1])} lbs"
                day_text = f"{int(count)} lift" if count == 1 else f"{int(count)} lifts"
                hover_text[i, j] = f"{time_range}<br>{weight_range}<br>{day_text}"

    # 9) Build Heatmap
    fig = go.Figure(
        data=go.Heatmap(
            x=xcenters,
            y=ycenters,
            z=H.T,  # Transpose to match Plotly's row-column convention
            colorscale=plotly_colorscale,
            colorbar=dict(title="Count"),
            zmin=0,  # Ensure valid range for colormap
            text=hover_text.T,  # Transpose to align with z=H.T
            hovertemplate="%{text}<extra></extra>",  # Use custom hover text
        )
    )

    # 10) Update layout with formatted time labels
    fig.update_layout(
        #increase title font size
        title=dict(
            text="Time of Day vs. Top Set Weight",
            font=dict(size=12)
        ),
        xaxis=dict(
            title="Time (AM/PM)",
            tickmode="array",
            tickvals=xcenters,
            title_font = dict(size=12),
            ticktext=time_labels,  # Use AM/PM formatted labels
            range=[time_min, time_max],
            tickfont=dict(size=12) 

        ),
        yaxis=dict(
            title=f"{weight_col} (lbs)",
            title_font=dict(size=12),
            tickfont=dict(size=12) 
        ),
        #template="plotly_white",
        #template="plotly_dark",
        template="plotly_dark",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
    )

    return fig
