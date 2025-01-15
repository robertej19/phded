from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px
from charts.boolean_grip_heatmap import create_boolean_grip_heatmap

# Load data
df = pd.read_csv("local_data.csv")

# Create app
app = Dash(__name__)
server = app.server

# Layout
app.layout = html.Div([
    dcc.Graph(id="boolean-heatmap", figure=create_boolean_grip_heatmap(df)),
    dcc.Graph(id="day-vs-weight-scatter")
])

# Callback
@app.callback(
    Output("day-vs-weight-scatter", "figure"),
    Input("boolean-heatmap", "hoverData")
)
def update_scatter(hover_data):
    if hover_data is None:
        # Default scatter plot if no hover
        return px.scatter(
            df,
            x="Day Number",
            y="Effective Weight",
            title="Day vs. Effective Weight",
            template="plotly_white"
        )

    # Extract indices from hoverData
    point = hover_data["points"][0]
    indices = point["customdata"]

    # Filter data based on indices
    filtered_df = df.loc[indices]

    # Create scatter plot
    fig = px.scatter(
        filtered_df,
        x="Day Number",
        y="Effective Weight",
        hover_data=["Time", "Grip"],
        title="Filtered: Day vs. Effective Weight",
        template="plotly_white"
    )
    return fig

# Run server
if __name__ == "__main__":
    app.run_server(debug=True)
