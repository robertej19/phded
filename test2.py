import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import sys

# -------------------------------------------------------------------------
# 1) Load local CSV
# -------------------------------------------------------------------------
df = pd.read_csv("local_data.csv")
# -------------------------------------------------------------------------
# 2) Parse "Time" column to a continuous numeric scale (decimal hours)
#    e.g., 0700 -> 7.00, 1315 -> 13.25, etc.
# -------------------------------------------------------------------------
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


#remove rows with no time
df = df.dropna(subset=["Time"])

# Ensure "Time" is string, then parse
df["Time"] = df["Time"].astype(str)
print(df["Time"])

df["DecimalHour"] = df["Time"].apply(to_decimal_hours)
print(df["DecimalHour"])

# For the mean weight on hover, pick a column that denotes "weight lifted".
# Adjust the name as needed (e.g., "Average Weight" or "Top Set Weight" etc.).
weight_col = "Average Weight"
if weight_col not in df.columns:
    # If your sheet has a different weight column, adjust here or skip
    df[weight_col] = np.nan

# Drop rows without a valid DecimalHour
df = df.dropna(subset=["DecimalHour"])
print(df)
# -------------------------------------------------------------------------
# 3) Manually bin the data and compute:
#    - Count per bin
#    - Mean weight per bin
# -------------------------------------------------------------------------
# Define bin edges (e.g., every 0.5 hours => 48 bins per day, or 1h => 24 bins)
# You can choose your resolution. Here, 24 bins for each hour boundary:
bin_edges = np.arange(0, 25, 1)  # [0,1,2,...,24]
bin_indices = np.digitize(df["DecimalHour"], bin_edges) - 1  # which bin each row goes in

# Prepare arrays for bar chart
bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])  # midpoint of each bin
counts = np.zeros(len(bin_centers), dtype=int)
mean_weights = np.zeros(len(bin_centers), dtype=float)

# For each bin, gather the subset and compute count, mean weight
for i in range(len(bin_centers)):
    subset = df[bin_indices == i]
    counts[i] = len(subset)
    if len(subset) > 0:
        mean_weights[i] = subset[weight_col].mean()
    else:
        mean_weights[i] = np.nan

# -------------------------------------------------------------------------
# 4) Build a Plotly figure
#    - X-axis: bin_centers (continuous from 0..24)
#    - Y-axis: count
#    - Hover: show mean weight for that bin
# -------------------------------------------------------------------------
fig_time_hist = go.Figure(
    data=[
        go.Bar(
            x=bin_centers,
            y=counts,
            customdata=mean_weights,  # we store mean weight in customdata
            # Define a custom hover template:
            #   bin range, count, mean weight
            hovertemplate=(
                "Hour Bin Center: %{x:.1f}<br>"
                "Count: %{y}<br>"
                "Mean Weight: %{customdata:.2f}"
            ),
            width=0.8,  # adjusts the bar width (units ~ 1 hour)
        )
    ]
)

fig_time_hist.update_layout(
    title="Continuous Time Histogram (Military Format)",
    xaxis=dict(
        title="Decimal Hour (0=Midnight, 12=Noon, 23.999=11:59 PM)",
        range=[0, 24],  # ensures full 0..24 range visible
    ),
    yaxis=dict(title="Count"),
    template="plotly_white",
)

# -------------------------------------------------------------------------
# 5) Build a minimal Dash app
# -------------------------------------------------------------------------
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            dbc.Col(
                html.H1("Debug: 1D Time Histogram", className="text-center mt-4"),
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(
                dcc.Graph(figure=fig_time_hist),
                width=12
            )
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
