import pandas as pd
import plotly.express as px

def create_time_hist_figure(df: pd.DataFrame):
    """
    Creates and returns a 1D histogram of the 'Time' column.
    """
    # Convert 'Time' to numeric if needed
    if "Time" in df.columns:
        df["Time"] = pd.to_numeric(df["Time"], errors="coerce")

    fig = px.histogram(
        df,
        x="Time",
        nbins=20,
        title="Time of Day of Lifts",
    )
    fig.update_layout(
        xaxis_title="Time (Military)",
        yaxis_title="Count",
        template="plotly_white"
    )
    return fig
