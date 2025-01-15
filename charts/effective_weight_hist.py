import pandas as pd
import plotly.express as px

def create_effective_weight_figure(df: pd.DataFrame):
    """
    Scatter plot of Day Number vs. Average Weight.
    """
    fig = px.scatter(
        df,
        x="Day Number",
        y="Effective Weight",
        hover_data=["Time", "Grip"],
        title="Day vs. Effective Top Set Weight"
    )
    fig.update_layout(
        xaxis_title="Day Number",
        yaxis_title="Effective Weight",
        template="plotly_white"
    )
    return fig
