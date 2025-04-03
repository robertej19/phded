# charts/multi_weight_scatter.py

import pandas as pd
import plotly.graph_objects as go
import math
import datetime
import pandas as pd

def create_multi_weight_scatter(df: pd.DataFrame) -> go.Figure:
    """
    Builds a figure with 4 scatter traces of:
      1) Effective Weight
      2) Average Weight
      3) Top Set Weight
      4) Number of Reps (on a secondary y-axis)

    - No legend in the plot (showlegend=False).
    - All traces start with low opacity, letting us toggle them on/off externally.
    - Updated fonts to be larger for readability on any device.
    """

    # Ensure needed columns
    needed_cols = [
        "Day Number", "Time", "Grip",
        "Effective Weight", "Average Weight",
        "Top Set Weight", "Number of Reps"
    ]
    for col in needed_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Convert "Day Number" into actual dates
    # Day Number 1 corresponds to 2021-12-29
    xvals = pd.to_datetime("2021-12-29") + pd.to_timedelta(df["Day Number"] - 1, unit="D")


    def format_time(time_val):
        # Try converting time_val to a float
        try:
            numeric_time = float(time_val)
        except (ValueError, TypeError):
            return "N/A"
        # Check if the numeric value is NaN
        if math.isnan(numeric_time):
            return "N/A"
        # Convert to integer for formatting
        time_int = int(numeric_time)
        hour = time_int // 100
        minute = time_int % 100
        dt = datetime.time(hour, minute)
        formatted = dt.strftime("%I:%M %p")
        # Remove any leading zero, e.g., "04:24 PM" -> "4:24 PM"
        if formatted.startswith("0"):
            formatted = formatted[1:]
        return formatted



    # Custom hover text for additional info (only the time is now shown)
    def hover_text(i):
        formatted_time = format_time(df['Time'].iloc[i])
        return f"Time: {formatted_time}<br>"
    custom_hover = [hover_text(i) for i in range(len(df))]

    # Trace 1: Effective Weight
    trace_eff = go.Scatter(
        x=xvals,
        y=df["Effective Weight"],
        mode="markers",
        name="Effective Weight",
        marker=dict(opacity=1),
        text=custom_hover,
        hovertemplate=(
            "%{x|%B %d %Y}<br>"
            "Effective Weight: %{y:.0f}<br>"
            "%{text}<extra></extra>"
        ),
    )

    # Trace 2: Average Weight (smoothed curve)
    trace_avg = go.Scatter(
        x=xvals,
        y=df["Average Weight"],
        mode="lines",  # Connect points with a line
        name="Average Weight",
        text=custom_hover,
        hovertemplate=(
            "%{x|%B %d %Y}<br>"
            "Average Weight: %{y:.0f}<br>"
            "%{text}<extra></extra>"
        ),
    )

    # Trace 3: Top Set Weight
    trace_top = go.Scatter(
        x=xvals,
        y=df["Top Set Weight"],
        mode="lines",
        name="Top Set Weight",
        marker=dict(opacity=1),
        text=custom_hover,
        hovertemplate=(
            "%{x|%B %d %Y}<br>"
            "Top Set Weight: %{y:.0f}<br>"
            "%{text}<extra></extra>"
        ),
    )

    # Trace 4: Number of Reps (secondary y-axis)
    trace_reps = go.Scatter(
        x=xvals,
        y=df["Number of Reps"],
        mode="markers",
        name="Number of Reps",
        marker=dict(opacity=1),
        text=custom_hover,
        hovertemplate=(
            "%{x|%B %d %Y}<br>"
            "Reps: %{y:.0f}<br>"
            "%{text}<extra></extra>"
        ),
        yaxis="y2"
    )

    # Build figure with all 4 traces
    fig = go.Figure(data=[trace_eff, trace_avg, trace_top, trace_reps])

    # Updated layout for enhanced readability across devices:
    fig.update_layout(
        showlegend=False,  # No legend in the plot
        template="plotly_dark",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        autosize=True,  # Allow automatic sizing for responsiveness
        font=dict(
            family="Arial, sans-serif",
            size=16,         # Global base font size (increased)
            color="#FFFFFF"  # High-contrast white text for dark background
        ),
        title=dict(
            text="Deadlifts Over Time",
            font=dict(
                size=28,     # Larger title font size
                color="#FFFFFF"
            ),
            x=0.5,          # Center the title
            xanchor='center'
        ),
        xaxis=dict(
            title=dict(
                text="Date",
                font=dict(
                    size=20,  # Larger x-axis title
                    color="#FFFFFF"
                )
            ),
            tickfont=dict(
                size=16,      # Larger tick labels
                color="#FFFFFF"
            ),
            tickformat="%B %Y",  # Display date in "Month Year" format
        ),
        yaxis=dict(
            title=dict(
                text="Weight (lbs)",
                font=dict(
                    size=20,  # Larger y-axis title
                    color="#FFFFFF"
                )
            ),
            tickfont=dict(
                size=16,      # Larger tick labels
                color="#FFFFFF"
            )
        ),
        yaxis2=dict(
            title=dict(
                text="Number of Reps",
                font=dict(
                    size=20,  # Larger secondary y-axis title
                    color="#FFFFFF"
                )
            ),
            tickfont=dict(
                size=16,      # Larger tick labels for secondary y-axis
                color="#FFFFFF"
            ),
            overlaying="y",
            side="right",
            showgrid=False  # Remove horizontal grid lines for the secondary y-axis
        )
    )

    return fig
