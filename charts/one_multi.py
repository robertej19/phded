# charts/multi_weight_scatter.py

import pandas as pd
import plotly.graph_objects as go
def create_multi_weight_scatter(df: pd.DataFrame) -> go.Figure:
    """
    Builds a figure with 4 scatter traces of:
      1) Effective Weight
      2) Average Weight
      3) Top Set Weight
      4) Number of Reps (on a secondary y-axis)

    - No legend in the plot (showlegend=False).
    - All traces start with low opacity, letting us toggle them on/off externally.
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

    # Common x-axis
    xvals = df["Day Number"]

    # Custom hover text
    def hover_text(i):
        return f"Time: {df['Time'].iloc[i]}<br>Grip: {df['Grip'].iloc[i]}"
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
            "Day: %{x}<br>"
            "Effective Weight: %{y}<br>"
            "%{text}<extra></extra>"
        ),
    )

    # Trace 2: Average Weight (smoothed curve)
    trace_avg = go.Scatter(
        x=xvals,
        y=df["Average Weight"],
        mode="lines",  # Connect points with a line
        name="Average Weight",
        line_shape="spline",  # Add smoothing to the curve
        text=custom_hover,
        hovertemplate=(
            "Day: %{x}<br>"
            "Average Weight: %{y}<br>"
            "%{text}<extra></extra>"
        ),
    )



    # Trace 3: Top Set Weight
    trace_top = go.Scatter(
        x=xvals,
        y=df["Top Set Weight"],
        mode="markers",
        name="Top Set Weight",
        marker=dict(opacity=1),
        text=custom_hover,
        hovertemplate=(
            "Day: %{x}<br>"
            "Top Set Weight: %{y}<br>"
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
            "Day: %{x}<br>"
            "Reps: %{y}<br>"
            "%{text}<extra></extra>"
        ),
        yaxis="y2"
    )

    # Build figure with all 4 traces
    fig = go.Figure(data=[trace_eff, trace_avg, trace_top, trace_reps])



    fig.update_layout(
        showlegend=False,  # No legend in the plot
        xaxis_title="Day Number",
        #template="plotly_white",
        template="plotly_dark",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        

        
        font=dict(
            size=12,  # Increase font size globally
        ),
        title=dict(
            text="Comparison of Effective, Average, and Top Set",
            font=dict(size=12)  # Increase title font size
        ),
        xaxis=dict(
            title_font=dict(size=12),  # Increase x-axis title font size
            tickfont=dict(size=12)    # Increase x-axis tick font size
        ),
        yaxis=dict(
            title="Weight (lbs)",
            title_font=dict(size=12),  # Increase y-axis title font size
            tickfont=dict(size=12)    # Increase y-axis tick font size
        ),

        yaxis2=dict(
            title="Number of Reps",
            overlaying="y",
            side="right",
            showgrid=False  # Remove horizontal grid lines for the secondary y-axis
        )
    )
    return fig
