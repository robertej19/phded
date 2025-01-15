import pandas as pd
import plotly.express as px

def create_scatter_day_vs_avg(df: pd.DataFrame):
    """
    Scatter plot of Day Number vs. Average Weight.
    """
    fig = px.scatter(
        df,
        x="Day Number",
        y="Average Weight",
        hover_data=["Time", "Grip"],
        title="Day vs. Average Weight"
    )
    fig.update_layout(
        xaxis_title="Day Number",
        yaxis_title="Average Weight",
        template="plotly_white"
    )
    return fig
