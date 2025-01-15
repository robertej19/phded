import pandas as pd
import plotly.express as px

def create_top_set_figure(df: pd.DataFrame):
    """
    Scatter plot of Day Number vs. Average Weight.
    """
    fig = px.scatter(
        df,
        x="Day Number",
        y="Top Set Weight",
        hover_data=["Time", "Grip"],
        title="Day vs. Top Set Weight"
    )
    fig.update_layout(
        xaxis_title="Day Number",
        yaxis_title="Top Set Weight",
        template="plotly_white"
    )
    return fig
