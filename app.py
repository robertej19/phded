import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import pandas as pd
# 1) Import data loader
#this is just a test line
from utils.data import load_data, is_data_stale
import datetime
import os, sys
import os
import time
import numpy as np
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import pandas as pd
from charts.one_multi import create_multi_weight_scatter
import os
import dash
from dash import dcc, html

# 2) Import specific chart modules
from charts.two_time_vs_weight_2d import create_time_vs_weight_2d
from charts.three_time_vs_weight_circular import create_am_pm_radial_time_plot
from charts.four_day_vs_time_of_day import create_day_vs_time_of_day
from charts.five_rest_time import create_rest_time_histogram
from charts.one_multi import create_multi_weight_scatter
from charts.six_multibool import create_boolean_grip_heatmap
from charts.seven_oneday import create_histogram_with_toggles
from charts.eight_day_week_time import create_day_of_week_vs_weight_with_labels
from charts.eight_day_week_time import create_day_of_week_vs_time_am_pm
import sys

# Compute "Day number: X"
start_date = datetime.datetime(2021, 12, 29)
today = datetime.datetime.today()
delta = today - start_date
day_number = delta.days


# -------------------------------------------------------------------------
# 1) Config & Utilities
# -------------------------------------------------------------------------
CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1V0sk1rLHvYOfzpLnLOgzEi5eeOkRfzAHQqQ0AegjlOI"
    "/export?format=csv&gid=0"
)
LOCAL_CSV = "data/local_data.csv"

# -------------------------------------------------------------------------
# 2) Load/Cache Data
# -------------------------------------------------------------------------
if not is_data_stale(LOCAL_CSV):
    df = pd.read_csv(CSV_URL)
    df.to_csv(LOCAL_CSV, index=False)
else:
    df = pd.read_csv(LOCAL_CSV)

# Convert some columns to numeric if they exist
for col in ["Day Number", "Average Weight", "Top Set Weight", "Day"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")



df = df.dropna(subset=["Top Set Weight"])
print(df)
# Compute "Most Recent Lift: YxZ"
if 'Top Set Weight' in df.columns and 'Number of Reps' in df.columns:
    most_recent_weight = df['Top Set Weight'].iloc[-1]
    most_recent_reps = df['Number of Reps'].iloc[-1]
    print(most_recent_weight)
    print(most_recent_reps)
    most_recent_lift = f"{int(most_recent_weight)}lbs x{int(most_recent_reps)}"
    most_recent_date_raw = str(df['Date'].iloc[-1])  # Ensure it's a string
    most_recent_date = datetime.datetime.strptime(most_recent_date_raw, "%Y%m%d").strftime("%m.%d.%y")
else:
    most_recent_lift = "N/A"
# Compute "Total Weight Lifted: W"
if 'Top Set Weight' in df.columns and 'Number of Reps' in df.columns:
    total_weight_lifted = int((df['Top Set Weight'] * df['Number of Reps']).sum())
else:
    total_weight_lifted = "N/A"


# -------------------------------------------------------------------------
# Build Figures (calling each chart module)
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

number_of_empty_rows_before_today = day_number - len(df)

empty_rows_message = (
    html.P(
        f"Note: {number_of_empty_rows_before_today:,} lifts are not yet entered",
        className="text-center fs-4"  # fs-4 for larger text
    )
    if number_of_empty_rows_before_today != 0
    else None
)

#df["Rest"] = (24-last_days_lift)+Current_daysLift (all but first day)

#save df to csv
#df.to_csv("processed.csv")
# ... figure_top_set = create_top_set_figure(df), etc.


"""
############################
To Do
Plot weight & frequency & lifting time distribution vs day of the week!
PLOT DISTRIBUTION OF MINUTES - 0 to 59				

Fix bimodal guassian distribution
Fix Bingo plot, on hover = show selected points on # vs day plot (#1)
Fix Time of Day, if desired toggle switch for pure histogram vs circular heatmap // or linear heatmap

'answer the question - what new information do i convey by plotting this?'
"""
# 3) Define the Dash app
#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}]
)
server = app.server


# 4) Layout
# 4) Layout
app.layout = dbc.Container(
    fluid=True,
    className="fs-5",  # Increase font size everywhere
    children=[
        dbc.Row(
            dbc.Col(
                html.H1("Deadlift *Everyday*", className="text-center mt-4"),
                width=12
            )
        ),
        
        dbc.Row(
            dbc.Col(
                html.Div(
                    [


                        
                        html.P(
                            [
                                f"{day_number} Days",
                                html.Br(),
                                #html.Span(" | ", style={"margin": "0 20px"}),
                                f"Most Recent Lift: {most_recent_lift} on {most_recent_date}",
                                html.Br(),
                                #html.Span(" | ", style={"margin": "0 20px"}),
                                f"Cumulative Top Set Weight Lifted: {total_weight_lifted:,} lbs",
                            ],
                            className="text-center fs-4"  # fs-4 for larger text
                        ),



                        html.Div(
                            [
                                html.A(
                                    html.Img(
                                        src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png",
                                        alt="Instagram",
                                        style={"width": "30px", "height": "30px"}
                                    ),
                                    href="https://www.instagram.com/ph.d.e.d/",
                                    target="_blank",
                                    className="me-3"  # Add spacing between icons
                                ),
                                html.A(
                                    html.Img(
                                        src="https://upload.wikimedia.org/wikipedia/commons/4/42/YouTube_icon_%282013-2017%29.png",
                                        alt="YouTube",
                                        style={"width": "30px", "height": "30px"}
                                    ),
                                    href="https://www.youtube.com/channel/UC6ynxFCZgGhjlvV5C-8sJXQ",
                                    target="_blank",
                                    className="me-3"  # Add spacing between icons
                                ),
                                html.A(
                                    "Ψ",  # Greek symbol Psi
                                    href="https://superfluid.systems/",
                                    target="_blank",
                                    className="text-decoration-none fs-4",  # Larger font for Psi
                                    style={"color": "white", "text-decoration": "none"}  # Styling for Psi
                                )
                            ],
                            className="text-center mt-2"
                        ),
                    empty_rows_message  # Conditionally rendered message


                    ]
                ),
                width=12
            )




        ),

        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    id="multi-scatter-graph",
                    figure=fig_multi,
                     style={"width": "100%", "height": "auto"}
                    #style={"paddingLeft": "10%", "paddingRight": "10%", "height": "700px"}  # 10% L/R padding, taller plot
                ),
                width=12
            )
        ),

        html.Div(
            className="my-3 text-center",
            children=[
                dcc.Checklist(
                    id="metric-checklist",
                    options=[
                        {"label": "Effective Weight", "value": "Effective Weight"},
                        {"label": "Average Weight",   "value": "Average Weight"},
                        {"label": "Top Set Weight",   "value": "Top Set Weight"},
                        {"label": "Number of Reps",   "value": "Number of Reps"},
                    ],
                    value=["Average Weight"],
                    inline=True,
                    labelStyle={"margin-right": "10px"}  # Increased spacing between options
                )
            ]
        ),
        
        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    figure=fig_2d_hist,
                     style={"width": "100%", "height": "auto"}
                    #style={"paddingLeft": "10%", "paddingRight": "10%", "height": "700px"}
                ),
                width=12
            )
        ),

        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    figure=fig_time_circular,
                     style={"width": "100%", "height": "800px"}
                    #style={"paddingLeft": "10%", "paddingRight": "10%", "height": "700px"}
                ),
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    figure=fig_day_vs_time_of_day,
                     style={"width": "100%", "height": "auto"}
                    #style={"paddingLeft": "10%", "paddingRight": "10%", "height": "700px"}
                ),
                width=12
            )
        ),

        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    figure=fig_rest_time,
                     style={"width": "100%", "height": "auto"}
                    #style={"paddingLeft": "10%", "paddingRight": "10%", "height": "700px"}
                ),
                width=12
            )
        ),


        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    figure=fig_dwt,
                     style={"width": "100%", "height": "auto"}
                    #style={"paddingLeft": "10%", "paddingRight": "10%", "height": "700px"}
                ),
                width=12
            )
        ),

        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    figure=fig_dwt2,
                     style={"width": "100%", "height": "auto"}
                    #style={"paddingLeft": "10%", "paddingRight": "10%", "height": "700px"}
                ),
                width=12
            )
        ),

        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    figure=fig_oneday,
                     style={"width": "100%", "height": "auto"}
                    #style={"paddingLeft": "10%", "paddingRight": "10%", "height": "700px"}
                ),
                width=12
            )
        ),
        # dbc.Row(
        #     dbc.Col(
        #         dcc.Graph(
        #             figure=fig_bool,
        #             style={"paddingLeft": "10%", "paddingRight": "10%", "height": "700px"}
        #         ),
        #         width=12
        #     )
        # ),
        
        #add extra padding at the bottom
        html.Div(style={"padding": "400px 0"})

    ]
)


@app.callback(
    Output("multi-scatter-graph", "figure"),
    [Input("metric-checklist", "value")]
)
def toggle_traces(selected_metrics):
    # Start from the base figure
    fig = create_multi_weight_scatter(df)

    # The figure has 4 traces in this order:
    #  0: Effective Weight
    #  1: Average Weight
    #  2: Top Set Weight
    #  3: Number of Reps

    # A helper mapping trace index -> metric name
    trace_names = [
        "Effective Weight",
        "Average Weight",
        "Top Set Weight",
        "Number of Reps"
    ]

    # Adjust opacity of each trace
    for i, trace_name in enumerate(trace_names):
        if trace_name in selected_metrics:
            fig.data[i].opacity = 1.0
        else:
            fig.data[i].opacity = 0.0

    # Toggle visibility of the second y-axis based on "Number of Reps" selection
    if "Number of Reps" in selected_metrics:
        fig.update_layout(yaxis2=dict(visible=True))
    else:
        fig.update_layout(yaxis2=dict(visible=False))

    return fig


# 6) Run
# # # if __name__ == "__main__":
# # #    app.run_server(debug=True)

#if __name__ == "__main__":
#    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=False, host="0.0.0.0", port=port)
