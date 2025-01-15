# charts/multi_weight_scatter.py

import pandas as pd
import plotly.graph_objects as go

def create_multi_weight_scatter(df: pd.DataFrame):
    """
    Returns a figure with 4 scatter traces of:
      1) Effective Weight
      2) Average Weight
      3) Top Set Weight
      4) Number of Reps

    All plotted vs. "Day Number."

    A button selector lets you choose which dataset to highlight (opacity=1),
    while the others remain partially transparent (opacity=0.05).

    Hover text includes "Time" and "Grip" columns.
    """

    # Ensure the columns exist (Day Number, plus the 4 we want to plot)
    needed_cols = ["Day Number", "Time", "Grip",
                   "Effective Weight", "Average Weight",
                   "Top Set Weight", "Number of Reps"]
    for col in needed_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Common x-axis data
    xvals = df["Day Number"]

    # We'll store hover text in a reusable way
    # (You could make a more elaborate template if desired)
    def hover_text(i):
        return f"Time: {df['Time'].iloc[i]}<br>Grip: {df['Grip'].iloc[i]}"

    custom_hover = [hover_text(i) for i in range(len(df))]

    # Create 4 traces, each with a different y-axis column
    trace_eff = go.Scatter(
        x=xvals,
        y=df["Effective Weight"],
        mode="markers",
        name="Effective Weight",
        marker=dict(opacity=0.05),
        text=custom_hover,   # hover text
        hovertemplate=(
            "Day: %{x}<br>"
            "Effective Weight: %{y}<br>"
            "%{text}<extra></extra>"
        ),
    )

    trace_avg = go.Scatter(
        x=xvals,
        y=df["Average Weight"],
        mode="markers",
        name="Average Weight",
        marker=dict(opacity=0.05),
        text=custom_hover,
        hovertemplate=(
            "Day: %{x}<br>"
            "Average Weight: %{y}<br>"
            "%{text}<extra></extra>"
        ),
    )

    trace_top = go.Scatter(
        x=xvals,
        y=df["Top Set Weight"],
        mode="markers",
        name="Top Set Weight",
        marker=dict(opacity=0.05),
        text=custom_hover,
        hovertemplate=(
            "Day: %{x}<br>"
            "Top Set Weight: %{y}<br>"
            "%{text}<extra></extra>"
        ),
    )

    trace_reps = go.Scatter(
        x=xvals,
        y=df["Number of Reps"],
        mode="markers",
        name="Number of Reps",
        marker=dict(opacity=0.05),
        text=custom_hover,
        hovertemplate=(
            "Day: %{x}<br>"
            "Reps: %{y}<br>"
            "%{text}<extra></extra>"
        ),
    )

    # Combine all traces into one figure
    fig = go.Figure(data=[trace_eff, trace_avg, trace_top, trace_reps])

    # Define updatemenus (buttons) to switch which trace is highlighted
    # We'll update each trace's marker.opacity based on which button is clicked.
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.05,  # position of the button menu
                y=1.15,
                showactive=True,
                buttons=[
                    dict(
                        label="Effective Weight",
                        method="update",
                        args=[
                            {
                                "marker": [
                                    dict(opacity=1),   # trace_eff
                                    dict(opacity=0.05),# trace_avg
                                    dict(opacity=0.05),# trace_top
                                    dict(opacity=0.05) # trace_reps
                                ]
                            }
                        ],
                    ),
                    dict(
                        label="Average Weight",
                        method="update",
                        args=[
                            {
                                "marker": [
                                    dict(opacity=0.05),
                                    dict(opacity=1),
                                    dict(opacity=0.05),
                                    dict(opacity=0.05)
                                ]
                            }
                        ],
                    ),
                    dict(
                        label="Top Set Weight",
                        method="update",
                        args=[
                            {
                                "marker": [
                                    dict(opacity=0.05),
                                    dict(opacity=0.05),
                                    dict(opacity=1),
                                    dict(opacity=0.05)
                                ]
                            }
                        ],
                    ),
                    dict(
                        label="Number of Reps",
                        method="update",
                        args=[
                            {
                                "marker": [
                                    dict(opacity=0.05),
                                    dict(opacity=0.05),
                                    dict(opacity=0.05),
                                    dict(opacity=1)
                                ]
                            }
                        ],
                    ),
                ],
            )
        ]
    )

    # Final layout styling
    fig.update_layout(
        title="Day vs. Multiple Weight/Rep Metrics",
        xaxis_title="Day Number",
        yaxis_title="Value",
        template="plotly_white",
    )

    return fig
