import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import pandas as pd
# 1) Import data loader
from data import load_data
import datetime

# 2) Import specific chart modules
from charts.time_hist import create_time_hist_figure
from charts.day_vs_avg import create_scatter_day_vs_avg
from charts.time_vs_weight_2d import create_time_vs_weight_2d
from charts.top_set_hist import create_top_set_figure
from charts.effective_weight_hist import create_effective_weight_figure
from charts.time_vs_weight_circular import create_time_vs_weight_circular
from charts.three_day_vs_time_of_day import create_day_vs_time_of_day
from charts.four_rest_time import create_rest_time_histogram
from charts.five_multi import create_multi_weight_scatter
from charts.multibool import create_boolean_grip_heatmap
# Compute "Day number: X"
start_date = datetime.datetime(2021, 12, 28)
today = datetime.datetime.today()
delta = today - start_date
day_number = delta.days

# Suppose df is your DataFrame with 'DecimalHour' and 'Top Set Weight'.

# -------------------------------------------------------------------------
# Load the data once, so all charts can use the same DataFrame
# Replace with your actual CSV URL
# # # CSV_URL = (
# # #     "https://docs.google.com/spreadsheets/d/"
# # #     "1V0sk1rLHvYOfzpLnLOgzEi5eeOkRfzAHQqQ0AegjlOI"
# # #     "/export?format=csv&gid=0"
# # # )
# # # df = load_data(CSV_URL)
df = pd.read_csv("local_data.csv")
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
fig_time_hist = create_time_hist_figure(df)
fig_day_vs_avg = create_scatter_day_vs_avg(df)
fig_top_set_hist = create_top_set_figure(df)
fig_effective_weight = create_effective_weight_figure(df)
fig_multi = create_multi_weight_scatter(df)
fig_bool = create_boolean_grip_heatmap(df)
df = df.dropna(subset=["Time"])
print(df)
fig_2d_hist = create_time_vs_weight_2d(df)
fig_time_circular = create_time_vs_weight_circular(df)
fig_day_vs_time_of_day = create_day_vs_time_of_day(df)
fig_rest_time = create_rest_time_histogram(df)
#df["Rest"] = (24-last_days_lift)+Current_daysLift (all but first day)

#save df to csv
df.to_csv("processed.csv")
# ... figure_top_set = create_top_set_figure(df), etc.



"""
############################
Deadlift every day
Day Number | Most recent Lift | Total Weight Lifted at top Set
Instagram | Youtube | Homepage

#### DAYS HORIZONTAL AXIS
Raw topset - red
# of reps - blue
effective weight - purple
average weight - green
daily delta - yellow
smoothed delta - orange
time of day lifted - black

#### Circular Time of Day
toggle switch for pure histogram vs circular heatmap // or linear heatmap

### 1D rest histogram
### tile plot of beltless deficiet stiff bar other/mixed/straps - 4x6 bingo grid, on hover = show selected points on # vs day plot (#1)


"""

# -------------------------------------------------------------------------
# Create Dash App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server  # For deployment if needed


# Layout with multiple rows, each containing a chart
app.layout = dbc.Container(
    fluid=True,
       children=[
        dbc.Row(
            dbc.Col(
                html.H1("Deadlift *Everyday*", className="text-center mt-4"),
                width=12
            )
        ),
        
        dbc.Row(
            dbc.Col(
                html.P(
                    f"Day Number: {day_number} | Most Recent Lift: {most_recent_lift} on {most_recent_date} | Cumulative Weight Lifted : {total_weight_lifted:,} lbs",
                    className="text-center"
                ),
                width=12
            )
        ),

        dbc.Row(
            dbc.Col(
                dcc.Graph(figure=fig_multi),
                width=12
            )
        ),


        dbc.Row(
            dbc.Col(
                dcc.Graph(figure=fig_bool),
                width=12
            )
        ),


        dbc.Row(
            dbc.Col(
                dcc.Graph(figure=fig_day_vs_time_of_day),
                width=12
            )
        ),
        
        dbc.Row(
            dbc.Col(
                dcc.Graph(figure=fig_top_set_hist),
                width=12
            )
        ),

        dbc.Row(
            dbc.Col(
                dcc.Graph(figure=fig_effective_weight),
                width=12
            )
        ),

        dbc.Row(
            dbc.Col(
                dcc.Graph(figure=fig_rest_time),
                width=12
            )
        ),

        dbc.Row(
            dbc.Col(
                dcc.Graph(figure=fig_day_vs_avg),
                width=12
            )
        ),

        dbc.Row(
            dbc.Col(
                dcc.Graph(figure=fig_time_hist),
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(
                dcc.Graph(figure=fig_2d_hist),
                width=12
            )
        ),

        dbc.Row(
            dbc.Col(
                dcc.Graph(figure=fig_time_circular),
                width=12
            )
        ),

    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
