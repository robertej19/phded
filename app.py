import os, sys, datetime, time, dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output

import pandas as pd
import numpy as np

# 2) Import specific chart modules
from charts.chart_1_multi import create_multi_weight_scatter
from charts.chart_2_time_vs_weight_2d import create_time_vs_weight_2d
from charts.chart_3_time_circles import create_am_pm_radial_time_plots
from charts.chart_4_day_vs_time import create_day_vs_time_of_day
from charts.chart_5_rest_time import create_rest_time_histogram
from charts.chart_6_day_week_time import create_day_of_week_vs_weight_with_labels
from charts.chart_6_day_week_time import create_day_of_week_vs_time_am_pm
from charts.chart_9_fft import create_fft_analysis
from charts.chart_10_color_coded_histogram import create_color_coded_histogram

from charts.six_multibool import create_boolean_grip_heatmap
from charts.chart_7_1D_histograms import create_histogram_with_toggles
from charts.chart_8_time_bingo import create_time_bingo

from utils.data import load_data, is_data_stale


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

# check if local csv exists
if not os.path.exists(LOCAL_CSV):
    print("Local CSV does not exist, creating it now...")
    df = load_data(CSV_URL)
    df.to_csv(LOCAL_CSV, index=False)
# -------------------------------------------------------------------------
# 2) Load/Cache Data
# -------------------------------------------------------------------------
if is_data_stale(LOCAL_CSV):
    df = pd.read_csv(CSV_URL)
    df.to_csv(LOCAL_CSV, index=False)
else:
    df = pd.read_csv(LOCAL_CSV)

df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
# Now filter out rows that contain either an empty string or "#VALUE!" in any column.
mask = df.apply(lambda row: not row.astype(str).isin(["", " ", "#VALUE!"]).any(), axis=1)
df = df[mask]

# Convert some columns to numeric if they exist
for col in ["Day Number", "Average Weight", "Top Set Weight", "Day"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")




df = df.dropna(subset=["Top Set Weight"])

# Compute "Most Recent Lift: YxZ"
if 'Top Set Weight' in df.columns and 'Number of Reps' in df.columns:
    most_recent_weight = df['Top Set Weight'].iloc[-1]
    most_recent_reps = df['Number of Reps'].iloc[-1]
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
fig_time_circular_am,fig_time_circular_pm = create_am_pm_radial_time_plots(df2)
fig_day_vs_time_of_day = create_day_vs_time_of_day(df2)
fig_rest_time = create_rest_time_histogram(df2)

fig_color_hist = create_color_coded_histogram(df)

fig_fft = create_fft_analysis(df)

fig_dwt2 = create_day_of_week_vs_weight_with_labels(df)
fig_dwt = create_day_of_week_vs_time_am_pm(df)
fig_time_bingo, stat_results = create_time_bingo(df2)


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
	

Fix bimodal guassian distribution
Fix Bingo plot, on hover = show selected points on # vs day plot (#1)
Fix Time of Day, if desired toggle switch for pure histogram vs circular heatmap // or linear heatmap
Need to fix time parser off by one error - possibly issue due to daylight savings time
'answer the question - what new information do i convey by plotting this?'
"""
# 3) Define the Dash app
#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="PhDeD",
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
            [
                dbc.Col(
                    dcc.Graph(
                        id='graph-1',
                        figure=fig_time_circular_am,
                        className="responsive-graph"
                    ),
                    xs=12, sm=12, md=6, lg=6, xl=6  # Full width on xs/sm, half-width on md+
                ),
                dbc.Col(
                    dcc.Graph(
                        id='graph-2',
                        figure=fig_time_circular_pm,
                        className="responsive-graph"
                    ),
                    xs=12, sm=12, md=6, lg=6, xl=6
                ),
            ]
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

        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    figure=fig_color_hist,
                    style={"width": "100%", "height": "auto"}
                ),
                width=12
            )
        ),

        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    id="time-bingo-graph",
                    figure=fig_time_bingo,
                     style={"width": "100%", "height": "auto"}
                    #style={"paddingLeft": "10%", "paddingRight": "10%", "height": "700px"}  # 10% L/R padding, taller plot
                ),
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Div([
                    dcc.Graph(
                        id='fft-graph',
                        figure=fig_fft,
                        style={"width": "100%", "height": "auto"}
                    ),
                    html.H4("Select Date Range for Frequency Analysis", 
                           className="text-center mt-4 mb-2"),
                    dcc.RangeSlider(
                        id='fft-day-range',
                        min=df['Day Number'].min(),
                        max=df['Day Number'].max(),
                        step=1,
                        value=[df['Day Number'].min(), df['Day Number'].max()],
                        marks={
                            int(df['Day Number'].min()): {'label': 'Start', 'style': {'color': '#FFFFFF'}},
                            int(df['Day Number'].max()): {'label': 'End', 'style': {'color': '#FFFFFF'}}
                        },
                        allowCross=False
                    ),
                    html.Div(style={"height": "20px"})  # Add some bottom spacing
                ]),
                width=12
            )
        ),
dbc.Row(
    dbc.Col(
        html.Div([
            html.H4("Statistical Analysis of Lift Times", style={"fontWeight": "bold"}),
            html.P(
                "The chi-square test is a statistical method used to determine whether the observed distribution of data significantly differs "
                "from an expected theoretical distribution. The chi-square statistic quantifies the difference between observed and expected frequencies. "
                "The associated p-value represents the probability of observing data as extreme as the actual data, assuming that the null hypothesis "
                "(typically a uniform or specified distribution) is correct. A small p-value (commonly less than 0.05) provides evidence that the observed "
                "data deviate significantly from the expected distribution."
            ),
            html.P(
                "For example, the minute-level data were tested for uniformity across the 60 minutes within an hour. "
                f"The resulting chi-square statistic was {stat_results['minutes_uniform']['chi2']:.2f} with a p-value of "
                f"{stat_results['minutes_uniform']['p_value']:.3e}. Given this relatively large p-value, the data do not show "
                "significant deviation from a uniform distribution at the minute level."
            ),
            html.P(
                "In contrast, the hourly data were analyzed for uniformity across the 24 hours of the day. "
                f"This resulted in a chi-square statistic of {stat_results['hours_uniform']['chi2']:.2f} and a very small p-value "
                f"({stat_results['hours_uniform']['p_value']:.3e}), indicating strong evidence against uniform distribution. "
                "Thus, certain hours exhibit significantly higher lift activity than others."
            ),
            html.P(
                "Additionally, the hourly data were tested against a single Gaussian (normal) distribution characterized by the dataset's mean and "
                "standard deviation. This produced a chi-square statistic of "
                f"{stat_results['hours_gaussian']['chi2']:.2f} with a small p-value ({stat_results['hours_gaussian']['p_value']:.3e}), "
                "strongly suggesting that lift times do not conform to a simple Gaussian distribution."
            ),
            html.P(
                "Finally, Gaussian Mixture Models (GMM) were used to evaluate whether lift times exhibited multimodal patterns, "
                "meaning multiple distinct periods of increased lift activity throughout the day. Models with 1 to 5 Gaussian components "
                "were compared using the Bayesian Information Criterion (BIC), a metric balancing goodness-of-fit against model complexity. "
                f"The optimal model contained {stat_results['hours_multimodal']['best_n_components']} components, indicating multiple peaks of lift activity. "
                "The relative support for models with differing numbers of peaks was measured using differences in BIC values (ΔBIC), where larger positive ΔBIC values indicate less support. "
                "The ΔBIC values for each alternative model tested were: "
                f"{'; '.join([f'{n}-component: ΔBIC={delta_bic:.1f}' for n, delta_bic in stat_results['hours_multimodal']['delta_bic'].items() if n != stat_results['hours_multimodal']['best_n_components']])}. "
                "The identified peaks occur at approximately "
                f"{', '.join(f'{peak:.1f}' for peak in stat_results['hours_multimodal']['peaks'])} hours."
            ),
        ], style={"padding": "20px", "color": "#FFFFFF"}),
        width=12
    )
)


,
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
            # Restore the original hovertemplate if needed
            # (assuming you stored it or know what it should be)
        else:
            fig.data[i].opacity = 0.0
            # Completely disable hover for invisible traces
            fig.data[i].hoverinfo = 'none'
            fig.data[i].hoverlabel = None
            fig.data[i].hovertemplate = None


    # Toggle visibility of the second y-axis based on "Number of Reps" selection
    if "Number of Reps" in selected_metrics:
        fig.update_layout(yaxis2=dict(visible=True))
    else:
        fig.update_layout(yaxis2=dict(visible=False))

    return fig



@app.callback(
    Output("fft-graph", "figure"),
    [Input("fft-day-range", "value")]
)
def update_fft_plot(day_range):
    if day_range is None:
        day_range = [df['Day Number'].min(), df['Day Number'].max()]
    return create_fft_analysis(df, start_day=day_range[0], end_day=day_range[1])



# 6) Run
# # # if __name__ == "__main__":
# # #    app.run_server(debug=True)

#if __name__ == "__main__":
#    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=False, host="0.0.0.0", port=port)
