import pandas as pd
import plotly.express as px

def create_time_hist_figure(df: pd.DataFrame):
    """
    Creates and returns a 1D histogram of the 'Time' column with increased font sizes.
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
        template="plotly_white",
        font=dict(
            size=18,  # Increase font size globally
        ),
        title=dict(
            font=dict(size=24)  # Increase title font size
        ),
        xaxis=dict(
            title_font=dict(size=20),  # Increase x-axis title font size
            tickfont=dict(size=16)    # Increase x-axis tick font size
        ),
        yaxis=dict(
            title_font=dict(size=20),  # Increase y-axis title font size
            tickfont=dict(size=16)    # Increase y-axis tick font size
        )
    )
    return fig
