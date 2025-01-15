import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_time_vs_weight_circular(df: pd.DataFrame) -> go.Figure:
    """
    Create two circular histograms (polar plots) for AM (0-11.999 hours) and PM (12-23.999 hours),
    showing how many lifts occurred at each time bin.
    
    On hover, display a mini histogram-like 'popout' (ASCII style) of the 1D distribution
    of weight lifted during that time bin.
    
    Assumptions:
      - The DataFrame has a 'Time' column in military float (e.g., 1436.0)
        or string that can be converted similarly (e.g., '1436.0').
      - A 'Top Set Weight' column (or fallback to 'Average Weight') for the weight data.
      - A 'DecimalHour' column or we auto-calc it from 'Time'.
    """

    # 1) Identify which weight column to use
    weight_col = "Top Set Weight"
    if weight_col not in df.columns:
        weight_col = "Average Weight"
        if weight_col not in df.columns:
            raise ValueError("No valid weight column found (e.g., 'Top Set Weight' or 'Average Weight').")

    # 2) Convert 'Time' -> 'DecimalHour' if not already done
    def to_decimal_hours(mil_time_str):
        # Remove any ':'
        mil_time_str = mil_time_str.replace(":", "")
        try:
            val = int(float(mil_time_str))  # handles '1436.0'
            hh = val // 100
            mm = val % 100
            return hh + mm / 60.0
        except:
            return np.nan

    if "DecimalHour" not in df.columns:
        df["Time"] = df["Time"].astype(str)
        df["DecimalHour"] = df["Time"].apply(to_decimal_hours)

    # Drop rows missing time or weight
    df = df.dropna(subset=["DecimalHour", weight_col])

    # 3) Split data into AM (0 <= hour < 12) and PM (12 <= hour < 24)
    df_am = df[(df["DecimalHour"] >= 0) & (df["DecimalHour"] < 12)].copy()
    df_pm = df[(df["DecimalHour"] >= 12) & (df["DecimalHour"] < 24)].copy()

    # 4) Convert decimal hours -> angles in degrees, oriented so 12:00 is at angle=0 (top).
    #    We'll do a clockwise orientation by (angle = (450 - scaled) % 360).
    #    For AM, we map [0..12) -> [0..360). For PM, similarly but shift by subtracting 12 first.
    def angle_am(minutes):
        # AM range is 0..719 minutes -> 0..360 deg
        raw_angle = (minutes / 720.0) * 360.0
        return (450.0 - raw_angle) % 360.0

    def angle_pm(minutes):
        # PM range is 12..23.999 => 720..1439 minutes
        # Convert to [0..719], then same transform
        raw_angle = ((minutes - 720.0) / 720.0) * 360.0
        return (450.0 - raw_angle) % 360.0

    # 4A) Convert decimal hours to total minutes
    df_am["MinutesFromMidnight"] = (df_am["DecimalHour"] * 60.0).astype(int)
    df_pm["MinutesFromMidnight"] = (df_pm["DecimalHour"] * 60.0).astype(int)

    # 4B) For each subset, define angles
    df_am["Angle"] = df_am["MinutesFromMidnight"].apply(angle_am)
    df_pm["Angle"] = df_pm["MinutesFromMidnight"].apply(angle_pm)

    # 5) Bin the angles in 12 slices (30 deg each) or some resolution
    bins = np.linspace(0, 360, 13)  # 12 bins
    am_counts, am_edges = np.histogram(df_am["Angle"], bins=bins)
    pm_counts, pm_edges = np.histogram(df_pm["Angle"], bins=bins)

    # 5A) Midpoints for bar polar
    am_centers = 0.5 * (am_edges[:-1] + am_edges[1:])
    pm_centers = 0.5 * (pm_edges[:-1] + pm_edges[1:])

    # 6) For the 'popout' distribution on hover, we want a mini-hist of weight data
    #    in ASCII or small text form. We'll create a function that returns
    #    a quick ASCII bar for each bin in the angle histogram.
    #    We'll gather weight data in that angle bin and build a small distribution string.

    def mini_weight_hist(bin_df, bin_angle_low, bin_angle_high):
        """
        For the subset of bin_df where angle is in [bin_angle_low, bin_angle_high),
        gather 'weight_col' and build a mini distribution in ASCII.
        """
        # Tolerate the case where bin_angle_high < bin_angle_low if edges wrap around 360
        # We'll normalize angles to [0..360) before comparison.
        def in_range(angle):
            if bin_angle_low <= bin_angle_high:
                return (angle >= bin_angle_low) & (angle < bin_angle_high)
            else:
                # wrap around 360
                return (angle >= bin_angle_low) | (angle < bin_angle_high)

        subset = bin_df[in_range(bin_df["Angle"])]

        if subset.empty:
            return "No data"

        # We can do a quick grouping of weight data in 5-lb bins or just show stats
        # Let's do a simple approach: gather all weight values, round them,
        # then build a quick bar chart of frequencies (like 3 distinct bars).
        weights_rounded = subset[weight_col].round(-1)  # Round to nearest 10
        counts = weights_rounded.value_counts().sort_index()
        # Build a small ASCII bar chart
        lines = []
        for wval, c in counts.items():
            # e.g. "500 lbs | ****"
            bar = "*" * int(min(c, 10))  # cap to 10 stars to avoid big text
            lines.append(f"{int(wval)} lbs | {bar}")
        return "\n".join(lines)

    # Build text arrays for am/pm hover
    am_hover = []
    for i in range(len(am_centers)):
        low, high = am_edges[i], am_edges[i+1]
        # build ASCII plot
        ascii_plot = mini_weight_hist(df_am, low, high)
        # e.g. "Angle bin [xx, yy)\n <ASCII bars>"
        am_hover.append(f"Time bin: {int(low)}° - {int(high)}°\n{ascii_plot}")

    pm_hover = []
    for i in range(len(pm_centers)):
        low, high = pm_edges[i], pm_edges[i+1]
        ascii_plot = mini_weight_hist(df_pm, low, high)
        pm_hover.append(f"Time bin: {int(low)}° - {int(high)}°\n{ascii_plot}")

    # 7) Build 2 polar subplots: row=1, col=2
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "polar"}, {"type": "polar"}]],
        subplot_titles=["AM (0-11:59)", "PM (12:00-23:59)"]
    )

    # Barpolar for AM
    fig.add_trace(
        go.Barpolar(
            r=am_counts,
            theta=am_centers,
            width=30,  # each bin is 30 deg
            text=am_hover,
            hovertemplate="%{text}<extra></extra>",
            name="AM"
        ),
        row=1, col=1
    )

    # Barpolar for PM
    fig.add_trace(
        go.Barpolar(
            r=pm_counts,
            theta=pm_centers,
            width=30,
            text=pm_hover,
            hovertemplate="%{text}<extra></extra>",
            name="PM"
        ),
        row=1, col=2
    )

    # 8) Layout updates for each polar subplot
    fig.update_layout(
        title="Circular Time Plots (AM / PM) with Weight 'Popouts'",
        showlegend=False,
        polar=dict(
            radialaxis=dict(title="Count of Lifts", showticklabels=True),
            angularaxis=dict(
                direction="clockwise",
                rotation=0
            )
        ),
        polar2=dict(
            radialaxis=dict(title="Count of Lifts", showticklabels=True),
            angularaxis=dict(
                direction="clockwise",
                rotation=0
            )
        ),
        template="plotly_white"
    )

    return fig
