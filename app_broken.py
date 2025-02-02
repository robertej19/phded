import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import datetime
import os
import pandas as pd
from dash import Input, Output
from utils.data import load_data, is_data_stale
from charts.one_multi import create_multi_weight_scatter
from charts.two_time_vs_weight_2d import create_time_vs_weight_2d
from charts.three_time_vs_weight_circular import create_am_pm_radial_time_plot
from charts.four_day_vs_time_of_day import create_day_vs_time_of_day
from charts.five_rest_time import create_rest_time_histogram
from charts.six_multibool import create_boolean_grip_heatmap
from charts.seven_oneday import create_histogram_with_toggles
from charts.eight_day_week_time import create_day_of_week_vs_weight_with_labels, create_day_of_week_vs_time_am_pm

# Compute "Day number: X"
start_date = datetime.datetime(2021, 12, 29)
today = datetime.datetime.today()
delta = today - start_date
day_number = delta.days

# Load Data
CSV_URL = "https://docs.google.com/spreadsheets/d/1V0sk1rLHvYOfzpLnLOgzEi5eeOkRfzAHQqQ0AegjlOI/export?format=csv&gid=0"
LOCAL_CSV = "data/local_data.csv"
if not is_data_stale(LOCAL_CSV):
    df = pd.read_csv(CSV_URL)
    df.to_csv(LOCAL_CSV, index=False)
else:
    df = pd.read_csv(LOCAL_CSV)

# Clean and Prepare Data
for col in ["Day Number", "Average Weight", "Top Set Weight", "Day"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
df = df.dropna(subset=["Top Set Weight"])

# Calculate Metrics
if 'Top Set Weight' in df.columns and 'Number of Reps' in df.columns:
    most_recent_weight = df['Top Set Weight'].iloc[-1]
    most_recent_reps = df['Number of Reps'].iloc[-1]
    most_recent_lift = f"{int(most_recent_weight)}lbs x{int(most_recent_reps)}"
    most_recent_date_raw = str(df['Date'].iloc[-1])
    most_recent_date = datetime.datetime.strptime(most_recent_date_raw, "%Y%m%d").strftime("%m.%d.%y")
else:
    most_recent_lift = "N/A"
if 'Top Set Weight' in df.columns and 'Number of Reps' in df.columns:
    total_weight_lifted = int((df['Top Set Weight'] * df['Number of Reps']).sum())
else:
    total_weight_lifted = "N/A"

# Build Figures
fig_multi = create_multi_weight_scatter(df)
fig_bool = create_boolean_grip_heatmap(df)
fig_oneday = create_histogram_with_toggles(df)
df2 = df.dropna(subset=["Time"])
fig_2d_hist = create_time_vs_weight_2d(df2)
fig_time_circular = create_am_pm_radial_time_plot(df2)
fig_day_vs_time_of_day = create_day_vs_time_of_day(df2)
fig_rest_time = create_rest_time_histogram(df2)
fig_dwt2 = create_day_of_week_vs_weight_with_labels(df)
fig_dwt = create_day_of_week_vs_time_am_pm(df)

# Define the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}]
)
server = app.server
# Layout
app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            dbc.Col(html.H1("Deadlift *Everyday*", className="text-center mt-4"), width=12)
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.P(
                            [
                                f"{day_number} Days",
                                html.Br(),
                                f"Most Recent Lift: {most_recent_lift} on {most_recent_date}",
                                html.Br(),
                                f"Cumulative Top Set Weight Lifted: {total_weight_lifted:,} lbs",
                            ],
                            className="text-center fs-4",
                        ),
                        html.Div(
                            [
                                html.A(
                                    html.Img(
                                        src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png",
                                        alt="Instagram",
                                        style={"width": "30px", "height": "30px"},
                                    ),
                                    href="https://www.instagram.com/ph.d.e.d/",
                                    target="_blank",
                                    className="me-3",
                                ),
                                html.A(
                                    html.Img(
                                        src="https://upload.wikimedia.org/wikipedia/commons/4/42/YouTube_icon_%282013-2017%29.png",
                                        alt="YouTube",
                                        style={"width": "30px", "height": "30px"},
                                    ),
                                    href="https://www.youtube.com/channel/UC6ynxFCZgGhjlvV5C-8sJXQ",
                                    target="_blank",
                                    className="me-3",
                                ),
                                html.A(
                                    "Ψ",
                                    href="https://superfluid.systems/",
                                    target="_blank",
                                    className="text-decoration-none fs-4",
                                    style={"color": "white", "text-decoration": "none"},
                                ),
                            ],
                            className="text-center mt-2",
                        ),
                    ]
                ),
                width=12,
            )
        ),
        dbc.Row(
            dbc.Col(dcc.Graph(id="multi-scatter-graph", figure=fig_multi, style={"width": "100%", "height": "auto"}), width=12)
        ),
        dbc.Row(
            dbc.Col(dcc.Graph(figure=fig_2d_hist, style={"width": "100%", "height": "auto"}), width=12)
        ),
        
        dbc.Row([
            dbc.Col(
                dcc.Graph(figure=fig_time_circular, style={"height": "60vh", "width": "100%"}),
                width=12
            )
        ], className="my-4"),

        dbc.Row(
            dbc.Col(dcc.Graph(figure=fig_day_vs_time_of_day, style={"width": "100%", "height": "auto"}), width=12)
        ),
        dbc.Row(
            dbc.Col(dcc.Graph(figure=fig_rest_time, style={"width": "100%", "height": "auto"}), width=12)
        ),
        dbc.Row(
            dbc.Col(dcc.Graph(figure=fig_dwt, style={"width": "100%", "height": "auto"}), width=12)
        ),
        dbc.Row(
            dbc.Col(dcc.Graph(figure=fig_dwt2, style={"width": "100%", "height": "auto"}), width=12)
        ),
        dbc.Row(
            dbc.Col(dcc.Graph(figure=fig_oneday, style={"width": "100%", "height": "auto"}), width=12)
        ),
    ],
)

# Callbacks
@app.callback(
    Output("multi-scatter-graph", "figure"),
    [Input("metric-checklist", "value")],
)
def toggle_traces(selected_metrics):
    fig = create_multi_weight_scatter(df)
    trace_names = ["Effective Weight", "Average Weight", "Top Set Weight", "Number of Reps"]
    for i, trace_name in enumerate(trace_names):
        fig.data[i].opacity = 1.0 if trace_name in selected_metrics else 0.0
    fig.update_layout(yaxis2=dict(visible="Number of Reps" in selected_metrics))
    return fig

# # # Run
# # if __name__ == "__main__":
# #     port = int(os.environ.get("PORT", 8050))
# #     app.run_server(debug=True, host="0.0.0.0", port=port)
if __name__ == "__main__":
   app.run_server(debug=True)
