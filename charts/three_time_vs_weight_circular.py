import numpy as np
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def create_am_pm_radial_time_plot(df: pd.DataFrame) -> go.Figure:
    """
    Creates two radial (polar) plots side by side:
      - Left: 12 AM -> 11:59 AM (0..12 hours), divided into 48 bins (each bin=15 min).
      - Right: 12 PM -> 11:59 PM (12..24 hours), also 48 bins of 15 min each.

    Each 15-min bin extends radially based on how many lifts occurred in that quarter-hour.

    We label only on the hour increments (e.g., "12 AM", "1 AM", etc.),
    although there are four 15-min bins per hour. 

    Key Points:
      - 'DecimalHour' is in [0..24).
      - AM subset: [0..12), PM subset: [12..24).
      - For each subset, 12 hours * 4 bins/hour = 48 bins.
      - Each bin ~ 7.5° since 360° / 48 = 7.5.
      - Hour labels appear every 4 bins (one hour).
      - Both subplots share the same max radial range so you can compare them easily.
    """

    # -------------------------------------------------------------------------
    # 1) Convert 'Time' -> 'DecimalHour' if not already present
    # -------------------------------------------------------------------------
    def to_decimal_hours(mil_time_str: str) -> float:
        """Convert something like '1436.0' -> 14.6 decimal hours."""
        try:
            s = mil_time_str.replace(":", "")
            val = int(float(s))  # e.g., '1436.0' -> 1436 -> hh=14, mm=36
            hh = val // 100
            mm = val % 100
            return hh + mm / 60.0
        except:
            return np.nan

    if "DecimalHour" not in df.columns:
        df["Time"] = df["Time"].astype(str)
        df["DecimalHour"] = df["Time"].apply(to_decimal_hours)

    df = df.dropna(subset=["DecimalHour"])

    # -------------------------------------------------------------------------
    # 2) Split into AM (0 <= hr < 12) and PM (12 <= hr < 24)
    # -------------------------------------------------------------------------
    df_am = df[(df["DecimalHour"] >= 0) & (df["DecimalHour"] < 12)].copy()
    df_pm = df[(df["DecimalHour"] >= 12) & (df["DecimalHour"] < 24)].copy()

    # -------------------------------------------------------------------------
    # 3) Define quarter-hour bins:
    #    Each 1 hour => 4 bins, e.g. 0.00..0.25 => bin 0, 0.25..0.50 => bin 1, etc.
    # -------------------------------------------------------------------------
    def quarter_hour_bin(decimal_hr: float) -> int:
        """
        Convert a decimal hour (0..12) -> integer bin [0..47].
        Example: 1.2 hr => 4.8 => bin=4, roughly (1 hour 12 minutes).
        """
        return int(decimal_hr * 4)

    # For AM, range is [0..12), so bin => [0..48)
    df_am["QBin"] = df_am["DecimalHour"].apply(quarter_hour_bin)

    # For PM, subtract 12 so it ranges [0..12)
    def pm_quarter_hour_bin(decimal_hr: float) -> int:
        """DecimalHour in [12..24) => shift by 12 => [0..12). Then *4 => [0..48)."""
        return int((decimal_hr - 12.0) * 4)

    df_pm["QBin"] = df_pm["DecimalHour"].apply(pm_quarter_hour_bin)

    # -------------------------------------------------------------------------
    # 4) Count how many lifts per quarter-hour bin for AM and PM
    # -------------------------------------------------------------------------
    am_counts = df_am["QBin"].value_counts().sort_index()
    pm_counts = df_pm["QBin"].value_counts().sort_index()

    # Fill missing bins with 0 => range 0..47
    for b in range(48):
        if b not in am_counts:
            am_counts.loc[b] = 0
    am_counts = am_counts.sort_index()

    for b in range(48):
        if b not in pm_counts:
            pm_counts.loc[b] = 0
    pm_counts = pm_counts.sort_index()

    # Convert to arrays for radial distances
    am_counts_arr = am_counts.values
    pm_counts_arr = pm_counts.values

    # -------------------------------------------------------------------------
    # 5) Calculate angles for each 15-min bin:
    #    We have 48 bins => each bin = 7.5° => bin i => angle= i * 7.5
    # -------------------------------------------------------------------------
    n_bins = 48
    angle_step = 360.0 / n_bins  # 7.5
    angles = np.arange(n_bins) * angle_step  # 0, 7.5, 15, ..., 352.5

    # -------------------------------------------------------------------------
    # 6) Define tickvals/ticktext for hours
    #    Each hour has 4 quarter-hour bins. The label goes on the first bin.
    # -------------------------------------------------------------------------
    # AM hours => 0..11
    am_tickvals = []
    am_ticktext = []
    for hour in range(12):  # 0..11
        # The bin index for hour 'hour' is hour*4
        bin_index = hour * 4
        am_tickvals.append(bin_index * angle_step)
        # Format label => 12 AM if hour=0, else 1 AM..11 AM
        label = "12 AM" if hour == 0 else f"{hour} AM"
        am_ticktext.append(label)

    # PM hours => 0..11 (but conceptually 12..23)
    pm_tickvals = []
    pm_ticktext = []
    for i, hour in enumerate(range(12, 24)):  # 12..23
        # For PM subset, hour i in [0..11], but actual hour=12..23
        # bin_index = (hour-12)*4
        bin_index = (hour - 12) * 4
        angle = bin_index * angle_step
        pm_tickvals.append(angle)
        if hour == 12:
            pm_ticktext.append("12 PM")
        else:
            pm_ticktext.append(f"{hour-12} PM")

    # -------------------------------------------------------------------------
    # 7) Build the subplot with two polar charts
    # -------------------------------------------------------------------------
    fig = make_subplots(
        rows=2,
        cols=1,
        specs=[
            [{"type": "polar"}],
            [{"type": "polar"}]
        ],
        # subplot_titles=["First Polar Plot", "Second Polar Plot"]
    )


    fig.add_trace(
        go.Barpolar(
            r=am_counts_arr,
            theta=angles,
            width=angle_step,
            marker_color="blue",
            name="AM 15-min bins",
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Barpolar(
            r=pm_counts_arr,
            theta=angles,
            width=angle_step,
            marker_color="firebrick",
            name="PM 15-min bins",
        ),
        row=2, col=1
    )

    # -------------------------------------------------------------------------
    # 8) Set same max radial range for easier comparison
    # -------------------------------------------------------------------------
    max_val = float(max(am_counts_arr.max(), pm_counts_arr.max()))

    # -------------------------------------------------------------------------
    # 9) Update layout
    # -------------------------------------------------------------------------
    fig.update_layout(
        title=dict(
            text="Number of Lifts Across Time of Day",
            font=dict(size=12)  # Title font size
        ),
        showlegend=False,
        #template="plotly_white",
        #template="plotly_dark",
        template="plotly_dark",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        polar=dict(
            radialaxis=dict(
                showticklabels=False,  # Remove radial axis tick labels
                title=None,            # Remove radial axis title
                range=[0, max_val]
            ),
            angularaxis=dict(
                tickmode="array",
                tickvals=am_tickvals,
                ticktext=am_ticktext,
                tickfont=dict(size=12),  # Angular axis tick font size
                direction="clockwise",
                rotation=90  # 12:00 at top
            )
        ),
        polar2=dict(
            radialaxis=dict(
                showticklabels=False,  # Remove radial axis tick labels
                title=None,            # Remove radial axis title
                range=[0, max_val]
            ),
            angularaxis=dict(
                tickmode="array",
                tickvals=pm_tickvals,
                ticktext=pm_ticktext,
                tickfont=dict(size=12),  # Angular axis tick font size
                direction="clockwise",
                rotation=90
            )
        )
    )


    return fig
