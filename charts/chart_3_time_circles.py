import numpy as np
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import numpy as np
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def create_am_pm_radial_time_plot(df: pd.DataFrame) -> go.Figure:
    """
    Creates two radial (polar) plots arranged vertically:
      - Top: 12 AM -> 11:59 AM (0–12 hours), divided into 48 bins (each bin = 15 min).
      - Bottom: 12 PM -> 11:59 PM (12–24 hours), also divided into 48 bins.
    
    Each 15-min bin extends radially based on the number of lifts in that quarter-hour.
    Hour labels appear every 4 bins (i.e. every hour) and both plots share the same
    maximum radial range for easy comparison.
    
    On hover, the time slice for that bin and the number of lifts are displayed.
    
    Updates:
      - Larger, high-contrast fonts for all text elements.
      - Each polar plot is extended to use the full width of the figure.
    """
    # -------------------------------------------------------------------------
    # 1) Convert 'Time' -> 'DecimalHour' if not already present.
    # -------------------------------------------------------------------------
    def to_decimal_hours(mil_time_str: str) -> float:
        """Convert a military time string (e.g., '1436.0') to decimal hours."""
        try:
            s = mil_time_str.replace(":", "")
            val = int(float(s))  # e.g., '1436.0' -> 1436 (hh=14, mm=36)
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
    # 2) Split into AM (0 ≤ hr < 12) and PM (12 ≤ hr < 24)
    # -------------------------------------------------------------------------
    df_am = df[(df["DecimalHour"] >= 0) & (df["DecimalHour"] < 12)].copy()
    df_pm = df[(df["DecimalHour"] >= 12) & (df["DecimalHour"] < 24)].copy()

    # -------------------------------------------------------------------------
    # 3) Define quarter-hour bins (48 bins per 12 hours, each representing 15 minutes)
    # -------------------------------------------------------------------------
    def quarter_hour_bin(decimal_hr: float) -> int:
        """Convert a decimal hour in [0, 12) to an integer bin index [0, 47]."""
        return int(decimal_hr * 4)

    df_am["QBin"] = df_am["DecimalHour"].apply(quarter_hour_bin)

    def pm_quarter_hour_bin(decimal_hr: float) -> int:
        """For PM times (12 ≤ hr < 24), subtract 12 and convert to a quarter-hour bin [0, 47]."""
        return int((decimal_hr - 12.0) * 4)

    df_pm["QBin"] = df_pm["DecimalHour"].apply(pm_quarter_hour_bin)

    # -------------------------------------------------------------------------
    # 4) Count lifts per quarter-hour bin for AM and PM
    # -------------------------------------------------------------------------
    am_counts = df_am["QBin"].value_counts().sort_index()
    pm_counts = df_pm["QBin"].value_counts().sort_index()

    # Ensure all bins [0, 47] are present by filling missing bins with 0
    for b in range(48):
        if b not in am_counts:
            am_counts.loc[b] = 0
    am_counts = am_counts.sort_index()

    for b in range(48):
        if b not in pm_counts:
            pm_counts.loc[b] = 0
    pm_counts = pm_counts.sort_index()

    am_counts_arr = am_counts.values
    pm_counts_arr = pm_counts.values

    # -------------------------------------------------------------------------
    # 5) Calculate angles for each 15-min bin (each bin = 7.5° since 360°/48 = 7.5°)
    # -------------------------------------------------------------------------
    n_bins = 48
    angle_step = 360.0 / n_bins
    angles = np.arange(n_bins) * angle_step

    # -------------------------------------------------------------------------
    # 6) Define tick values and labels for hour markers (every 4 bins = 1 hour)
    # -------------------------------------------------------------------------
    # AM tick settings: Hours 0–11
    am_tickvals = []
    am_ticktext = []
    for hour in range(12):
        bin_index = hour * 4
        am_tickvals.append(bin_index * angle_step)
        label = "12 AM" if hour == 0 else f"{hour} AM"
        am_ticktext.append(label)

    # PM tick settings: Hours 12–23, but labels shown as "12 PM", "1 PM", etc.
    pm_tickvals = []
    pm_ticktext = []
    for hour in range(12, 24):
        bin_index = (hour - 12) * 4
        pm_tickvals.append(bin_index * angle_step)
        label = "12 PM" if hour == 12 else f"{hour-12} PM"
        pm_ticktext.append(label)

    # -------------------------------------------------------------------------
    # 7) Create custom hover text for each quarter-hour bin.
    # -------------------------------------------------------------------------
    # Helper to convert a decimal hour to an AM/PM string.
    def decimal_hour_to_ampm(decimal_hour):
        hour = int(decimal_hour)
        minute = int(round((decimal_hour - hour) * 60))
        period = "AM" if decimal_hour < 12 else "PM"
        hour_12 = hour % 12
        hour_12 = 12 if hour_12 == 0 else hour_12
        return f"{hour_12}:{minute:02d} {period}"

    def quarter_bin_to_time_range_am(bin_index):
        start = bin_index / 4.0
        end = (bin_index + 1) / 4.0
        return f"{decimal_hour_to_ampm(start)} - {decimal_hour_to_ampm(end)}"

    def quarter_bin_to_time_range_pm(bin_index):
        start = bin_index / 4.0 + 12
        end = (bin_index + 1) / 4.0 + 12
        return f"{decimal_hour_to_ampm(start)} - {decimal_hour_to_ampm(end)}"

    # Build custom data arrays for hover text.
    am_customdata = [quarter_bin_to_time_range_am(i) for i in range(n_bins)]
    pm_customdata = [quarter_bin_to_time_range_pm(i) for i in range(n_bins)]

    # -------------------------------------------------------------------------
    # 8) Create the subplot with two polar charts arranged vertically
    # -------------------------------------------------------------------------
    from plotly.subplots import make_subplots
    fig = make_subplots(
        rows=2,
        cols=1,
        specs=[[{"type": "polar"}],
               [{"type": "polar"}]]
    )

    # Add AM trace with custom hover data.
    fig.add_trace(
        go.Barpolar(
            r=am_counts_arr,
            theta=angles,
            width=angle_step,
            marker_color="green",
            name="AM 15-min bins",
            customdata=am_customdata,
            hovertemplate="Time: %{customdata}<br>Lifts: %{r}<extra></extra>"
        ),
        row=1, col=1
    )

    # Add PM trace with custom hover data.
    fig.add_trace(
        go.Barpolar(
            r=pm_counts_arr,
            theta=angles,
            width=angle_step,
            marker_color="firebrick",
            name="PM 15-min bins",
            customdata=pm_customdata,
            hovertemplate="Time: %{customdata}<br>Lifts: %{r}<extra></extra>"
        ),
        row=2, col=1
    )

    # -------------------------------------------------------------------------
    # 9) Set the same maximum radial range for both polar plots for easy comparison
    # -------------------------------------------------------------------------
    max_val = float(max(am_counts_arr.max(), pm_counts_arr.max()))

    # -------------------------------------------------------------------------
    # 10) Update layout with larger fonts and extended polar domains
    # -------------------------------------------------------------------------
    fig.update_layout(
        autosize=True,
        font=dict(
            family="Arial, sans-serif",
            size=16,
            color="#FFFFFF"
        ),
        title=dict(
            text="Number of Lifts Across Time of Day",
            font=dict(size=28, color="#FFFFFF")
        ),
        showlegend=False,
        template="plotly_dark",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        polar=dict(
            radialaxis=dict(
                showticklabels=False,
                title=None,
                range=[0, max_val]
            ),
            angularaxis=dict(
                tickmode="array",
                tickvals=am_tickvals,
                ticktext=am_ticktext,
                tickfont=dict(size=22, color="#FFFFFF"),
                direction="clockwise",
                rotation=90
            )
        ),
        polar2=dict(
            radialaxis=dict(
                showticklabels=False,
                title=None,
                range=[0, max_val]
            ),
            angularaxis=dict(
                tickmode="array",
                tickvals=pm_tickvals,
                ticktext=pm_ticktext,
                tickfont=dict(size=22, color="#FFFFFF"),
                direction="clockwise",
                rotation=90
            )
        )
    )

    return fig
