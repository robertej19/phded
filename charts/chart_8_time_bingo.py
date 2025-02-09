import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys

def create_time_bingo(df: pd.DataFrame) -> go.Figure:


    df["Hour"] = df["DecimalHour"].astype(int)
    df["Minute"] = ((df["DecimalHour"] - df["Hour"]) * 60).round().astype(int)


    # ------------------------------
    # Group by Hour and Minute to Count Occurrences
    # ------------------------------
    # ------------------------------
    # Group by Hour and Minute to Count Occurrences
    # ------------------------------
    grouped = df.groupby(['Hour', 'Minute']).size()
    # Create a 24×60 DataFrame (rows: hours 0–23, columns: minutes 0–59).
    heatmap_data = grouped.unstack(level='Minute').reindex(index=range(24), columns=range(60))

    # --------------------------------
    # Additional Calculations for Title
    # --------------------------------
    total_possible = 24 * 60  # 1440 possible unique hour-minute cells.
    non_zero_count = np.sum(~np.isnan(heatmap_data.values))
    total_entries = len(df)
    unique_hours = df['Hour'].nunique()
    unique_minutes = df['Minute'].nunique()

    # --------------------------------
    # Marginal Histograms Data
    # --------------------------------
    # For the bottom marginal (minute distribution) and left marginal (hour distribution)
    minute_totals = heatmap_data.sum(axis=0, skipna=True)  # Sum over hours (for each minute)
    hour_totals   = heatmap_data.sum(axis=1, skipna=True)  # Sum over minutes (for each hour)

    # --------------------------------
    # Custom Hover Text for the Main Heatmap
    # --------------------------------
    hover_text = []
    for hour in heatmap_data.index:

        row_text = []
        for minute in heatmap_data.columns:
            count = heatmap_data.loc[hour, minute]
            if pd.isna(count):
                row_text.append("")
            else:
                hour_text = hour
                minute_text = minute
                if hour_text < 10:
                    hour_text = f"0{hour}"
                if minute_text < 10:
                    minute_text = f"0{minute}"

                row_text.append(f"Time: {hour_text}:{minute_text}<br>Lifts: {int(count)}")
        hover_text.append(row_text)

    # --------------------------------
    # Create the Figure with Marginals on Left and Bottom
    # --------------------------------
    # Layout grid (2 rows x 2 columns):
    # - (1,2): Main heatmap
    # - (1,1): Left marginal: hours distribution (shared y-axis with the main heatmap)
    # - (2,2): Bottom marginal: minutes distribution (shared x-axis with the main heatmap)
    # - (2,1): (Empty)
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "bar"}, {"type": "heatmap"}],
            [None, {"type": "bar"}]],
        shared_yaxes=True,  # Share y-axis between left marginal and main heatmap
        shared_xaxes=True,  # Share x-axis between main heatmap and bottom marginal
        #subplot_titles=("Distribution of time of lift – hours", "", "Distribution of time of lift – minutes"),
        row_heights=[0.8, 0.2],
        column_widths=[0.1, 0.9],
        horizontal_spacing=0.02,
        vertical_spacing=0.02
    )

    #choose a predefined colormap that works well on dark background that isn't viridis
    dark_colormap = 'viridis'
    # --------------------------------
    # Add the Main Heatmap (Row 1, Col 2)
    # --------------------------------
    heatmap_trace = go.Heatmap(
        z=heatmap_data.values,
        x=list(heatmap_data.columns),  # Minutes (0–59)
        y=list(heatmap_data.index),    # Hours (0–23)
        colorscale=dark_colormap,
        text=hover_text,
        hovertemplate="%{text}<extra></extra>",
        showscale=False  # Remove the colorbar
    )
    fig.add_trace(heatmap_trace, row=1, col=2)

    # --------------------------------
    # Add the Left Marginal: Hour Distribution (Row 1, Col 1)
    # --------------------------------
    # Use a horizontal bar chart so that y corresponds to hours.
    hour_bar = go.Bar(
        x=hour_totals.values,           # Lifts count
        y=list(heatmap_data.index),      # Hours
        orientation='h',
        marker_color='gray',
        showlegend=False,
        hovertemplate="Hour: %{y}<br>Lifts: %{x}<extra></extra>"
    )
    fig.add_trace(hour_bar, row=1, col=1)

    # --------------------------------
    # Add the Bottom Marginal: Minute Distribution (Row 2, Col 2)
    # --------------------------------
    minute_bar = go.Bar(
        x=list(heatmap_data.columns),    # Minutes
        y=minute_totals.values,          # Lifts count
        marker_color='gray',
        showlegend=False,
        hovertemplate="Minute: %{x}<br>Lifts: %{y}<extra></extra>"
    )
    fig.add_trace(minute_bar, row=2, col=2)
    

    # --------------------------------
    # Update Axes Labels for the Main Heatmap
    # --------------------------------
    fig.update_xaxes(title_text="Minute of Hour", row=2, col=2)
    fig.update_yaxes(title_text="Hour of Day", row=1, col=1)
    fig.update_xaxes(autorange='reversed', row=1, col=1)
    fig.update_yaxes(autorange='reversed', row=2, col=2)


    # Optionally hide redundant tick labels on the marginals.
    fig.update_xaxes(showticklabels=False, row=1, col=1)  # Left marginal x-axis
    fig.update_yaxes(showticklabels=False, row=2, col=2)  # Bottom marginal y-axis

    #hide grid lines on row=2 col=2
    fig.update_yaxes(showgrid=False, row=2, col=2)
    fig.update_xaxes(showgrid=False, row=1, col=1)


    # --------------------------------
    # Update Overall Layout Title and Margins
    # --------------------------------
    fig.update_layout(
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
            text= f"Bingo Chart of Lift Clock Times: <br> {non_zero_count}/{total_possible} Times Recorded",
            font=dict(
                size=28,     # Larger title font size
                color="#FFFFFF"
            ),
            #center the title
            x=0.5
        ),
        margin=dict(l=60, r=60, t=100, b=60)
    )



    return fig
