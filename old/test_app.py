import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc

# Load local CSV data (must be in the same folder or provide full path)
df = pd.read_csv("local_data.csv")
#Get first 10 rows only 
df = df.head(10)

# Convert the "Time" column to numeric if needed
# (Assuming "Time" is stored in military format like 1838 for 6:38 PM)
df["Time"] = pd.to_numeric(df["Time"], errors="coerce")

# Create a simple histogram of the "Time" column
fig_time_hist = px.histogram(
    df,
    x="Time",
    nbins=20,
    title="Histogram of 'Time' Column"
)

fig_time_hist.update_layout(
    xaxis_title="Time (Military Format)",
    yaxis_title="Count",
    template="plotly_white"
)

# Build Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            dbc.Col(
                html.H1("Debug: Local CSV Time Histogram", className="text-center mt-4"),
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
