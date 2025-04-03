import plotly.graph_objects as go
import numpy as np

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
        {"label": "Top Set Weight",      "col": "Top Set Weight"},
        {"label": "Average Weight",      "col": "Average Weight"},
        {"label": "Effective Weight",    "col": "Effective Weight"},
    ]

    # Metrics that require x-axis limits to be set to 400-600
    metrics_with_custom_xlim = {"Top Set Weight", "Average Weight", "Effective Weight"}

    # 2) Create a trace for each metric
    fig = go.Figure()

    for i, m in enumerate(metrics):
        col_name = m["col"]
        # Only build the trace if the column exists in df
        if col_name not in df.columns:
            continue

        if col_name == "Number of Reps":
            # Manually compute histogram bins so we can set custom hover text
            data = df[col_name]
            # Create integer bins covering the range of rep counts
            bin_min = int(data.min())
            bin_max = int(data.max())
            bin_edges = list(range(bin_min, bin_max + 2))
            counts, bins = np.histogram(data, bins=bin_edges)
            # Use the left edge of each bin as the x value
            bin_values = bins[:-1]
            # Create custom hover text: "1 rep" if 1, otherwise "X reps"
            custom_text = [f"{x} rep" if x == 1 else f"{x} reps" for x in bin_values]

            fig.add_trace(
                go.Bar(
                    x=bin_values,
                    y=counts,
                    name=m["label"],
                    visible=True if i == 0 else False,
                    opacity=0.6,
                    hovertemplate="%{customdata}<br>%{y:.0f} lifts<extra></extra>",
                    customdata=custom_text
                )
            )
        else:
            # For the other metrics, use a Histogram trace with a standard hover template
            hover_template = "%{x:.0f} lbs<br>%{y:.0f} lifts<extra></extra>"
            fig.add_trace(
                go.Histogram(
                    x=df[col_name],
                    name=m["label"],
                    visible=True if i == 0 else False,  # Show only the first trace by default
                    opacity=0.6,  # Slight transparency so overlapping histograms can be seen
                    nbinsx=20,    # Set number of bins
                    hovertemplate=hover_template,
                )
            )

    # 3) Create updatemenus (buttons) for toggling traces
    buttons = []
    for i, m in enumerate(metrics):
        # Build a list of True/False values for each trace (only the current one is visible)
        visible_array = [False] * len(metrics)
        visible_array[i] = True

        # Prepare layout updates for the current trace
        layout_updates = {
            "xaxis.title.text": m["label"],
            "title": f"Distribution of {m['label']}"
        }

        # Set custom x- and y-axis ranges for certain metrics
        if m["label"] in metrics_with_custom_xlim:
            layout_updates["xaxis.range"] = [400, 600]
            layout_updates["yaxis.range"] = [0, 180]
        else:
            # Default ranges for other metrics
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
                direction="down",       # You can change to "left" for horizontal layout
                showactive=True,
                x=1.15,                 # Adjust placement as needed
                y=0.5,
                xanchor="left",
                yanchor="middle",
                font=dict(
                    color="black",      # Button text color
                    size=12             # Button text font size
                ),
            )
        ],
        title="Distribution of Number of Reps",
        font=dict(
            family="Arial, sans-serif",
            size=18,         # Increased global base font size
            color="#FFFFFF"  # White text for dark theme
        ),
        barmode="overlay",  # So multiple histogram traces can overlap
        template="plotly_dark",      # Dark theme
        paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
    )

    # Optional: Further axis formatting with increased font sizes
    fig.update_xaxes(
        title_text="Value",
        title_font=dict(size=20, color="#FFFFFF"),
        tickfont=dict(size=16, color="#FFFFFF")
    )
    fig.update_yaxes(
        title_text="Number of Lifts",
        title_font=dict(size=20, color="#FFFFFF"),
        tickfont=dict(size=16, color="#FFFFFF")
    )

    return fig
