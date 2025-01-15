import os
import time
import numpy as np
import pandas as pd

from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#Earliest lift as a function of time

# -------------------------------------------------------------------------
# 1) Config & Utilities
# -------------------------------------------------------------------------
CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1V0sk1rLHvYOfzpLnLOgzEi5eeOkRfzAHQqQ0AegjlOI"
    "/export?format=csv&gid=0"
)
LOCAL_CSV = "local_data.csv"
ONE_DAY_IN_SECONDS = 86400

def is_data_stale(file_path):
    """Return True if local file doesn't exist or is older than one day."""
    if not os.path.exists(file_path):
        return True
    file_age = time.time() - os.path.getmtime(file_path)
    return file_age > ONE_DAY_IN_SECONDS

# -------------------------------------------------------------------------
# 2) Load/Cache Data
# -------------------------------------------------------------------------
if is_data_stale(LOCAL_CSV):
    df = pd.read_csv(CSV_URL)
    df.to_csv(LOCAL_CSV, index=False)
else:
    df = pd.read_csv(LOCAL_CSV)

# Convert some columns to numeric if they exist
for col in ["Day Number", "Average Weight", "Top Set Weight", "Day"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# -------------------------------------------------------------------------
# 3) Build Figures
# -------------------------------------------------------------------------

# 3.1 Scatter Plot: Day Number vs. Average Weight (with Time, Grip in hover)
fig_scatter = px.scatter(
    df,
    x="Day Number",
    y="Top Set Weight",
    hover_data=["Time", "Grip"],  # shows Time and Grip in tooltip
    title="Average Weight Over Time",
)
fig_scatter.update_layout(
    xaxis_title="Day Number",
    yaxis_title="Average Weight",
    template="plotly_white",
)


# 3.1 Scatter Plot: Day Number vs. Average Weight (with Time, Grip in hover)
fig_scatter2 = px.scatter(
    df,
    x="Day Number",
    y="Number of Reps",
    hover_data=["Time", "Grip"],  # shows Time and Grip in tooltip
    title="Reps Over Time",
)
fig_scatter2.update_layout(
    xaxis_title="Day Number",
    yaxis_title="Number of Reps",
    template="plotly_white",
)

# 3.2 Histogram of "Top Set Weight"
if "Top Set Weight" in df.columns:
    fig_hist_topset = px.histogram(
        df,
        x="Top Set Weight",
        nbins=50,
        title="Histogram of Top Set Weight",
    )
    fig_hist_topset.update_layout(
        xaxis_title="Top Set Weight",
        yaxis_title="Count",
        template="plotly_white",
    )
else:
    fig_hist_topset = go.Figure()
    fig_hist_topset.add_annotation(
        text="No 'Top Set Weight' column found.",
        showarrow=False
    )

# 3.3 2D Histogram (Day vs. Top Set Weight) using a density heatmap
if "DayNumber" in df.columns and "Effective Weight" in df.columns:
    fig_2d = px.density_heatmap(
        df,
        x="DayNumber",
        y="Effective Weight",
        title="2D Histogram: Day vs. Top Set Weight",
        nbinsx=10,
        nbinsy=50,
    )
    fig_2d.update_layout(
        xaxis_title="Day",
        yaxis_title="Top Set Weight",
        template="plotly_white",
    )
else:
    fig_2d = go.Figure()
    fig_2d.add_annotation(
        text="Missing 'Day' or 'Top Set Weight' column.",
        showarrow=False
    )

if "Time" in df.columns:
    # Clean up "Time" (remove any colons) and convert to integer if possible
    df["Time"] = df["Time"].astype(str).str.replace(":", "", regex=False)
    df["TimeInt"] = pd.to_numeric(df["Time"], errors="coerce").fillna(0).astype(int)

    # Convert something like 1838 => 18:38 => total minutes from midnight = 18*60 + 38
    def to_minutes(t):
        hours = t // 100
        mins = t % 100
        return hours * 60 + mins

    df["MinutesFromMidnight"] = df["TimeInt"].apply(to_minutes)

    # Split into AM/PM subsets
    am_data = df[df["TimeInt"] < 1200].copy()   # 0000-1159
    pm_data = df[df["TimeInt"] >= 1200].copy() # 1200-2359

    # Map [0..719] or [720..1439] -> angles [0..360], with 12:00 at top (angle=0 or 360)
    # We do angle = (450 - scaled_minutes) mod 360 so times increase clockwise.
    def angle_am(m):
        # m in [0..719], scale to [0..360]
        raw_angle = (m / 720.0) * 360.0
        return (450.0 - raw_angle) % 360.0

    def angle_pm(m):
        # m in [720..1439], subtract 720 to shift to [0..719], then scale
        raw_angle = ((m - 720) / 720.0) * 360.0
        return (450.0 - raw_angle) % 360.0

    am_angles = am_data["MinutesFromMidnight"].apply(angle_am)
    pm_angles = pm_data["MinutesFromMidnight"].apply(angle_pm)

    # Bin each set of angles in 12 slices (30° each)
    bins = np.linspace(0, 360, 13)  # [0, 30, 60, ..., 360]
    am_counts, am_edges = np.histogram(am_angles, bins=bins)
    pm_counts, pm_edges = np.histogram(pm_angles, bins=bins)

    # Midpoints for each bin
    am_centers = 0.5 * (am_edges[:-1] + am_edges[1:])
    pm_centers = 0.5 * (pm_edges[:-1] + pm_edges[1:])

    fig_circ = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "polar"}, {"type": "polar"}]],
        subplot_titles=["AM (0000 - 1159)", "PM (1200 - 2359)"],
    )

    fig_circ.add_trace(
        go.Barpolar(
            theta=am_centers,
            r=am_counts,
            name="AM",
            marker_color="royalblue",
        ),
        row=1, col=1
    )
    fig_circ.add_trace(
        go.Barpolar(
            theta=pm_centers,
            r=pm_counts,
            name="PM",
            marker_color="firebrick",
        ),
        row=1, col=2
    )

    # Define tick labels for a 'normal clock' proceeding clockwise:
    # 12:00 at angle=0, 3:00 at angle=270, 6:00 at angle=180, 9:00 at angle=90
    # We'll space them 30° apart but label them as hour marks.
    # For the AM subplot:
    am_tickvals = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
    #  12 AM, 11 AM, 10 AM, 9 AM, ... going clockwise from top
    #  We can map these systematically, but here’s a manual example:
    am_ticktext = [
        "12:00", "11:00", "10:00", "9:00", "8:00", "7:00",
        "6:00", "5:00", "4:00", "3:00", "2:00", "1:00"
    ]

    # For the PM subplot:
    pm_tickvals = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
    pm_ticktext = [
        "12:00", "11:00", "10:00", "9:00", "8:00", "7:00",
        "6:00", "5:00", "4:00", "3:00", "2:00", "1:00"
    ]

    fig_circ.update_layout(
        title="Circular Histograms for Time (Clock-Oriented, Military Input)",
        showlegend=False,
        polar=dict(
            radialaxis=dict(showticklabels=True),
            angularaxis=dict(
                tickmode="array",
                tickvals=am_tickvals,
                ticktext=am_ticktext,
                direction="clockwise",
                rotation=0,  # angle at which 0 tick is placed (top)
            ),
        ),
        polar2=dict(
            radialaxis=dict(showticklabels=True),
            angularaxis=dict(
                tickmode="array",
                tickvals=pm_tickvals,
                ticktext=pm_ticktext,
                direction="clockwise",
                rotation=0,
            ),
        ),
    )
else:
    fig_circ = go.Figure()
    fig_circ.add_annotation(text="No 'Time' column found.", showarrow=False)


# -------------------------------------------------------------------------
# 4) Build Dash App
# -------------------------------------------------------------------------
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server  # Expose the server if deploying

app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            dbc.Col(
                html.H1("Dashboard", className="text-center mt-4"),
                width=12
            )
        ),

        # Scatter: Day Number vs. Average Weight
        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    figure=fig_scatter,
                    style={"height": "500px"}
                ),
                width=12,
            )
        ),

                # Scatter: Day Number vs. Average Weight
        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    figure=fig_scatter2,
                    style={"height": "500px"}
                ),
                width=12,
            )
        ),

        # Histogram of Top Set Weight
        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    figure=fig_hist_topset,
                    style={"height": "500px"}
                ),
                width=12,
            )
        ),

        # 2D Histogram (Day vs. Top Set Weight)
        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    figure=fig_2d,
                    style={"height": "500px"}
                ),
                width=12,
            )
        ),

        # Circular Histograms for Time
        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    figure=fig_circ,
                    style={"height": "600px"}
                ),
                width=12,
            )
        ),
    ],
)

# -------------------------------------------------------------------------
# 5) Run the Server
# -------------------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=True)

