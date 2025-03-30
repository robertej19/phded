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

    # 1) Determine which weight column to use (customize as needed)
    weight_col = "Top Set Weight"
    if weight_col not in df.columns:
        weight_col = "Average Weight"
        if weight_col not in df.columns:
            raise ValueError("No valid weight column found (e.g., 'Top Set Weight' or 'Average Weight').")

    # Ensure "Time" is a string and convert to DecimalHour
    df["Time"] = df["Time"].astype(str)
    print(df["Time"])
    df["DecimalHour"] = df["Time"].apply(to_decimal_hours)

    # 2) Drop rows with invalid time or weight data
    df = df.dropna(subset=["DecimalHour", weight_col])

    # 3) Prepare bin edges for time and weight
    time_min, time_max = 0, 24
    time_bin_width = 1.0
    time_bins = np.arange(time_min, time_max + time_bin_width, time_bin_width)

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
    # Set zeros to NaN for better visualization (bad values rendered as white)
    H = np.where(H == 0, np.nan, H)

    # 5) Define bin centers for the heatmap
    xcenters = 0.5 * (xedges[:-1] + xedges[1:])
    ycenters = 0.5 * (yedges[:-1] + yedges[1:])

    # 6) Create a Plotly colorscale from a matplotlib colormap (viridis)
    viridis = plt.cm.viridis.copy()
    viridis.set_bad("white")  # Set NaN values to white
    plotly_colorscale = [
        [i / 255.0, f"rgb({r},{g},{b})"]
        for i, (r, g, b, _) in enumerate((viridis(np.linspace(0, 1, 256)) * 255).astype(int))
    ]

    # 7) Format time bins in AM/PM format
    def decimal_hour_to_ampm(decimal_hour):
        hour = int(decimal_hour)
        minute = int(round((decimal_hour - hour) * 60))
        period = "AM" if hour < 12 else "PM"
        hour = hour % 12
        hour = 12 if hour == 0 else hour
        return f"{hour}:{minute:02d} {period}"
    
    # Only display every third label for clarity
    time_labels = [decimal_hour_to_ampm(x) if i % 3 == 0 else "" for i, x in enumerate(xcenters)]

    # 8) Create hover text for each bin as a 2D array
    hover_text = np.full(H.shape, "", dtype=object)
    for i in range(len(xcenters)):  # Iterate over time bins
        for j in range(len(ycenters)):  # Iterate over weight bins
            count = H[i, j]
            if not np.isnan(count):
                time_range = f"{decimal_hour_to_ampm(xedges[i])} - {decimal_hour_to_ampm(xedges[i + 1])}"
                weight_range = f"{int(yedges[j])} - {int(yedges[j + 1])} lbs"
                day_text = f"{int(count)} lift" if count == 1 else f"{int(count)} lifts"
                hover_text[i, j] = f"{time_range}<br>{weight_range}<br>{day_text}"

    # 9) Build the Heatmap
    fig = go.Figure(
        data=go.Heatmap(
            x=xcenters,
            y=ycenters,
            z=H.T,  # Transpose to match Plotly's row-column convention
            colorscale=plotly_colorscale,
            colorbar=dict(
                title=dict(
                    text="Count",
                    font=dict(size=16, color="#FFFFFF")
                ),
                tickfont=dict(size=16, color="#FFFFFF")
            ),
            zmin=0,
            text=hover_text.T,  # Transpose to align with z
            hovertemplate="%{text}<extra></extra>",
        )
    )

    # 10) Update layout with enhanced, responsive font settings
    fig.update_layout(
        autosize=True,
        font=dict(
            family="Arial, sans-serif",
            size=16,         # Global base font size
            color="#FFFFFF"  # High-contrast for dark template
        ),
        title=dict(
            text="Time of Day vs. Top Set Weight",
            font=dict(
                size=28,     # Larger title font size
                color="#FFFFFF"
            )
        ),
        xaxis=dict(
            title=dict(
                text="Time (AM/PM)",
                font=dict(size=20, color="#FFFFFF")
            ),
            tickmode="array",
            tickvals=xcenters,
            ticktext=time_labels,
            range=[time_min, time_max],
            tickfont=dict(size=16, color="#FFFFFF")
        ),
        yaxis=dict(
            range=[400, 600],
            title=dict(
                text=f"{weight_col} (lbs)",
                font=dict(size=20, color="#FFFFFF")
            ),
            tickfont=dict(size=16, color="#FFFFFF")
        ),
        template="plotly_dark",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)"
    )

    return fig
