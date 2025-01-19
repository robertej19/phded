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
        {"label": "Number of Reps",    "col": "Number of Reps"},
        {"label": "Top Set Weight",   "col": "Top Set Weight"},
        {"label": "Average Weight",   "col": "Average Weight"},
        {"label": "Effective Weight", "col": "Effective Weight"},
    ]

    # Metrics that require x-axis limits to be set to 400-600
    metrics_with_custom_xlim = {"Top Set Weight", "Average Weight", "Effective Weight"}

    # 2) Create a histogram trace for each metric
    fig = go.Figure()

    for i, m in enumerate(metrics):
        col_name = m["col"]

        # Only build the trace if the column exists in df
        if col_name not in df.columns:
            continue

        # Build the histogram trace with customized hover labels
        fig.add_trace(
            go.Histogram(
                x=df[col_name],
                name=m["label"],
                visible=True if i == 0 else False,  # Show only the first trace by default
                opacity=0.6,  # Slight transparency so overlapping hist can be seen
                nbinsx=20,     # Set number of bins
                hovertemplate="%{x0} - %{x1} %{name}<br>%{y} lifts",  # Customized hover label
            )
        )

    # 3) Create updatemenus (buttons) for toggling traces
    # Each button toggles a single trace "visible", hiding the others
    buttons = []
    for i, m in enumerate(metrics):
        # We create a list of True/False for each trace
        visible_array = [False] * len(metrics)
        visible_array[i] = True  # Show the i-th trace

        # Prepare layout updates
        layout_updates = {
            "xaxis.title.text": m["label"],
            "title": f"Distribution of {m['label']}"
        }

        # Set x-axis and y-axis range if the metric requires it
        if m["label"] in metrics_with_custom_xlim:
            layout_updates["xaxis.range"] = [400, 600]
            layout_updates["yaxis.range"] = [0, 180]
        else:
            # Set default ranges for other metrics
            layout_updates["xaxis.range"] = [0, 10]
            layout_updates["yaxis.range"] = [0, 500]

        buttons.append(
            dict(
                label=m["label"],
                method="update",
                args=[
                    {"visible": visible_array},
                    layout_updates
                ],
            )
        )

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=buttons,
                direction="down",       # or "left", if you want horizontal
                showactive=True,
                x=1.15,                 # adjust placement as needed
                y=0.5,
                xanchor="left",
                yanchor="middle",
                font=dict(
                    color="black",      # Button text color
                    size=24             # Button text font size
                ),
            )
        ],
        title="Distribution of Parameters",
        font=dict(
            size=24  # Increase font size everywhere
        ),
        barmode="overlay",  # So multiple hist traces can overlap
        template="plotly_dark",      # if you want a dark theme
        paper_bgcolor="rgba(0,0,0,0)",  # transparent backgrounds
        plot_bgcolor="rgba(0,0,0,0)",
    )

    # (Optional) further axis formatting
    fig.update_xaxes(title_text="Value")
    fig.update_yaxes(title_text="Number of Lifts")

    return fig
