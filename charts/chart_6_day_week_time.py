import numpy as np
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

def create_day_of_week_vs_time_am_pm(df: pd.DataFrame) -> go.Figure:
    """
    Creates a 2D histogram (Heatmap) of Day of Week (x-axis) vs Time of Day (y-axis).
      - Time of Day is binned in half-hour increments (0.5 hr).
      - The x-axis day labels are centered on their bins.
      - Hover labels display "Monday<br>9:00 AM - 9:30 AM<br>N lifts".
    """
    # --------------------
    # 1) Prepare Data
    # --------------------
    df["Date"] = pd.to_datetime(df["Date"], format="%Y%m%d", errors="coerce")
    df["DayOfWeek"] = df["Date"].dt.weekday  # Monday=0 ... Sunday=6

    # Parse "Time" into decimal hours
    def to_decimal_hours(t_str):
        if not isinstance(t_str, str):
            t_str = str(t_str)
        t_str = t_str.replace(":", "")
        try:
            val = int(float(t_str))
            hh = val // 100
            mm = val % 100
            return hh + mm / 60.0
        except:
            return np.nan

    df["Time"] = df["Time"].astype(str)
    df["DecimalHour"] = df["Time"].apply(to_decimal_hours)

    # Keep only valid rows
    df = df.dropna(subset=["DayOfWeek", "DecimalHour"])

    # --------------------
    # 2) Define Bins
    # --------------------
    # Day bins: integer edges [0..7], meaning Monday=0..Sunday=6
    day_bins = np.arange(0, 8, 1)
    # Time bins: 0..24 in half-hour increments
    time_bins = np.arange(0, 24.5, 0.5)

    # --------------------
    # 3) 2D Histogram
    # --------------------
    H, xedges, yedges = np.histogram2d(
        x=df["DayOfWeek"],
        y=df["DecimalHour"],
        bins=[day_bins, time_bins]
    )
    # Convert 0 -> np.nan for better display
    H = np.where(H == 0, np.nan, H)

    # --------------------
    # 4) Colormap
    # --------------------
    viridis = plt.cm.viridis.copy()
    viridis.set_bad("white")  # For NaNs
    viridis_colors = [
        [i / 255.0, f"rgb({r},{g},{b})"]
        for i, (r, g, b, a) in enumerate((viridis(np.linspace(0, 1, 256)) * 255).astype(int))
    ]

    # --------------------
    # 5) Bin Centers & Labels
    # --------------------
    xcenters = 0.5 * (xedges[:-1] + xedges[1:])  # day-of-week centers
    ycenters = 0.5 * (yedges[:-1] + yedges[1:])  # time-of-day centers

    day_labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Helper to format decimal hours as HH:MM AM/PM
    def decimal_hour_to_ampm(decimal_hour):
        hour = int(decimal_hour)
        minute = int(round((decimal_hour - hour) * 60))
        period = "AM" if hour < 12 else "PM"
        # If hour == 24, reset to 0
        if hour == 24:
            hour = 0
            period = "AM"
        hour_12 = hour % 12
        hour_12 = 12 if hour_12 == 0 else hour_12
        return f"{hour_12}:{minute:02d} {period}"

    # --------------------
    # 6) Build Hover Text (2D)
    # --------------------
    hover_text = []
    for j in range(len(ycenters)):      # y-axis index
        row_text = []
        # Time range for the j-th bin
        time_start = decimal_hour_to_ampm(yedges[j])
        time_end   = decimal_hour_to_ampm(yedges[j+1])
        for i in range(len(xcenters)):  # x-axis index
            # Day label from day index (e.g., 0.5 -> day=0 => Monday)
            day_index = int(xcenters[i])
            day_str = day_labels[day_index] if 0 <= day_index < len(day_labels) else "Unknown"
            count = H[i, j]
            count_str = "0 lifts" if np.isnan(count) else f"{int(count)} lifts"
            row_text.append(f"{day_str}<br>{time_start} - {time_end}<br>{count_str}")
        hover_text.append(row_text)

    # --------------------
    # 7) Plotly Figure
    # --------------------
    fig = go.Figure(data=go.Heatmap(
        x=xcenters,
        y=ycenters,
        z=H.T,  # Transposed for correct orientation
        colorscale=viridis_colors,
        colorbar=dict(
            title="Count",
            title_font=dict(size=16, color="#FFFFFF"),
            tickfont=dict(size=16, color="#FFFFFF")
        ),
        hoverinfo="text",
        text=hover_text  # 2D list matching z
    ))

    # Only show y-axis ticks every 4 hours: 0, 4, 8, 12, 16, 20, 24
    tickvals_4h = np.arange(0, 25, 4)
    ticktext_4h = [decimal_hour_to_ampm(t) for t in tickvals_4h]

    # --------------------
    # 8) Update Layout with Larger Fonts and Transparent Backgrounds
    # --------------------
    fig.update_layout(
        autosize=True,
        title=dict(
            text="Day of Week vs. Time of Day",
            font=dict(size=28, color="#FFFFFF")
        ),
        xaxis=dict(
            tickmode="array",
            tickvals=xcenters,
            ticktext=day_labels,
            title=dict(text="Day of Week", font=dict(size=20, color="#FFFFFF")),
            tickfont=dict(size=16, color="#FFFFFF"),
            range=[0, 7.0]
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=tickvals_4h,
            ticktext=ticktext_4h,
            title=dict(text="Time of Day", font=dict(size=20, color="#FFFFFF")),
            tickfont=dict(size=16, color="#FFFFFF"),
            range=[0, 24]
        ),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", size=18, color="#FFFFFF")
    )

    return fig


def create_day_of_week_vs_weight_with_labels(df: pd.DataFrame) -> go.Figure:
    """
    Creates a 2D histogram (Heatmap) of Day of Week (x-axis) vs Top Set Weight (y-axis),
    with centered day labels and custom hover labels in the form:
      Monday<br>Weight: 425 lbs<br>N lifts
    The y-axis is limited to 400..600 lbs.
    """
    # --------------------
    # 1) Prepare Data
    # --------------------
    df["Date"] = pd.to_datetime(df["Date"], format="%Y%m%d", errors="coerce")
    df["DayOfWeek"] = df["Date"].dt.weekday  # Monday=0..Sunday=6

    # Keep only valid rows
    df = df.dropna(subset=["DayOfWeek", "Top Set Weight"])

    # --------------------
    # 2) Define Bins
    # --------------------
    day_bins = np.arange(0, 8, 1)                # 0..7 integer edges
    weight_bins = np.arange(400, 610, 10)          # 400..600 in 10-lb steps

    # --------------------
    # 3) 2D Histogram
    # --------------------
    H, xedges, yedges = np.histogram2d(
        x=df["DayOfWeek"],
        y=df["Top Set Weight"],
        bins=[day_bins, weight_bins]
    )
    H = np.where(H == 0, np.nan, H)

    # --------------------
    # 4) Colormap
    # --------------------
    viridis = plt.cm.viridis.copy()
    viridis.set_bad("white")
    viridis_colors = [
        [i / 255.0, f"rgb({r},{g},{b})"]
        for i, (r, g, b, a) in enumerate((viridis(np.linspace(0, 1, 256)) * 255).astype(int))
    ]

    # --------------------
    # 5) Bin Centers & Labels
    # --------------------
    xcenters = 0.5 * (xedges[:-1] + xedges[1:])  # day-of-week centers
    ycenters = 0.5 * (yedges[:-1] + yedges[1:])  # weight centers

    day_labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # --------------------
    # 6) Build Hover Text (2D)
    # --------------------
    hover_text = []
    for j in range(len(ycenters)):       # y index
        row_text = []
        w_start = int(yedges[j])
        w_end   = int(yedges[j+1])
        for i in range(len(xcenters)):   # x index
            day_index = int(xcenters[i])
            day_str = day_labels[day_index] if 0 <= day_index < len(day_labels) else "Unknown"
            count = H[i, j]
            count_str = "0 lifts" if np.isnan(count) else f"{int(count)} lifts"
            row_text.append(f"{day_str}<br>Weight: {w_start} lbs<br>{count_str}")
        hover_text.append(row_text)

    # --------------------
    # 7) Plotly Figure
    # --------------------
    fig = go.Figure(data=go.Heatmap(
        x=xcenters,
        y=ycenters,
        z=H.T,            # Transpose for correct orientation
        colorscale=viridis_colors,
        colorbar=dict(
            title="Count",
            title_font=dict(size=16, color="#FFFFFF"),
            tickfont=dict(size=16, color="#FFFFFF")
        ),
        hoverinfo="text",
        text=hover_text    # 2D list of hover text
    ))

    # --------------------
    # 8) Update Layout with Larger Fonts and Transparent Backgrounds
    # --------------------
    fig.update_layout(
        autosize=True,
        title=dict(
            text="Day of Week vs. Top Set Weight",
            font=dict(size=28, color="#FFFFFF")
        ),
        xaxis=dict(
            tickmode="array",
            tickvals=xcenters,
            ticktext=day_labels,
            title=dict(text="Day of Week", font=dict(size=20, color="#FFFFFF")),
            tickfont=dict(size=16, color="#FFFFFF"),
            range=[0, 7.0]
        ),
        yaxis=dict(
            title=dict(text="Top Set Weight (lbs)", font=dict(size=20, color="#FFFFFF")),
            tickfont=dict(size=16, color="#FFFFFF"),
            range=[400, 600]
        ),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", size=18, color="#FFFFFF")
    )

    return fig
