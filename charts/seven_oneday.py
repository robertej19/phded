import plotly.graph_objects as go

def create_histogram_with_toggles(df):
    """
    Create a 1D histogram with togglable traces for:
      - Number of Reps
      - Top Set Weight
      - Average Weight
      - Effective Weight
    """

    # 1) Define which columns you want to show
    metrics = [
        {"label": "Number of Reps",   "col": "Number of Reps"},
        {"label": "Top Set Weight",  "col": "Top Set Weight"},
        {"label": "Average Weight",  "col": "Average Weight"},
        {"label": "Effective Weight","col": "Effective Weight"},
    ]

    # 2) Create a histogram trace for each metric
    fig = go.Figure()

    for i, m in enumerate(metrics):
        col_name = m["col"]

        # Only build the trace if the column exists in df
        if col_name not in df.columns:
            continue
        
        # Build the histogram trace
        fig.add_trace(
            go.Histogram(
                x=df[col_name],
                name=m["label"],
                visible=True if i == 0 else False,  # Show only the first trace by default
                opacity=0.6,  # Slight transparency so overlapping hist can be seen
            )
        )

    # 3) Create updatemenus (buttons) for toggling traces
    # Each button toggles a single trace "visible", hiding the others
    buttons = []
    for i, m in enumerate(metrics):
        # We create a list of True/False for each trace
        visible_array = [False] * len(metrics)
        visible_array[i] = True  # Show the i-th trace
        buttons.append(
            dict(
                label=m["label"],
                method="update",
                args=[{"visible": visible_array},
                      {"title": f"Distribution of {m['label']}"}]
            )
        )

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=buttons,
                direction="down",       # or "left", if you want horizontal
                showactive=True,
                x=1.15,                 # adjust placement
                y=0.5,
                xanchor="left",
                yanchor="middle"
            )
        ],
        title="Distribution of Number of Reps (default)",
        barmode="overlay",  # So multiple hist traces can overlap
        template="plotly_dark",      # if you want a dark theme
        paper_bgcolor="rgba(0,0,0,0)",  # transparent backgrounds
        plot_bgcolor="rgba(0,0,0,0)",
    )

    # (Optional) further axis formatting
    fig.update_xaxes(title_text="Value")
    fig.update_yaxes(title_text="Count")

    return fig


# Example usage:
if __name__ == "__main__":
    import pandas as pd
    
    # Sample data
    data = {
        "Number of Reps": [5,5,5,3,2,8,12,5,6,5,8],
        "Top Set Weight": [135,185,225,225,225,255,275,315,185,135,225],
        "Average Weight": [100,140,200,210,210,230,250,270,140,110,220],
        "Effective Weight": [500,700,1000,675,450,1840,3300,945,600,355,1790],
    }
    df = pd.DataFrame(data)

    fig = create_histogram_with_toggles(df)
    fig.show()
