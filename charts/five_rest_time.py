# charts/rest_time_hist.py

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.mixture import GaussianMixture

def create_rest_time_histogram(df: pd.DataFrame):
    """
    1) Computes a new column 'Rest Time' in hours, representing the time between
       consecutive lifts on consecutive days.
    2) Plots a histogram of 'Rest Time' over 0..48 hours, bin size = 1 hour.
    3) Fits a 2-component Gaussian Mixture Model to 'Rest Time', then overlays:
       - Two separate Gaussian curves (one for each component).
       - A "Total PDF" curve showing the sum of the two components.
    4) Places the legend inside the chart, showing mixture parameters (means, stdevs, weights).
    """

    # ----------- 1) Check columns & sort data -----------
    required_cols = {"Day Number", "DecimalHour"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"DataFrame must contain {required_cols} columns.")

    # Sort by day number, then time
    df = df.sort_values(["Day Number", "DecimalHour"]).reset_index(drop=True)

    # ----------- 2) Compute 'Rest Time' -----------
    df["Rest Time"] = np.nan
    for i in range(1, len(df)):
        curr_day = df.loc[i, "Day Number"]
        prev_day = df.loc[i - 1, "Day Number"]
        curr_dec_hour = df.loc[i, "DecimalHour"]
        prev_dec_hour = df.loc[i - 1, "DecimalHour"]

        if curr_day == prev_day + 1:
            df.loc[i, "Rest Time"] = 24 - prev_dec_hour + curr_dec_hour

    # We only want rows that have a valid Rest Time
    hist_df = df.dropna(subset=["Rest Time"])

    # ----------- 3) Build the Histogram (0..48, 1-hr bins) -----------
    fig = px.histogram(
        hist_df,
        x="Rest Time",
        range_x=[0, 48],  # Force 0..48
        nbins=48,         # 1-hour bins
        title="Histogram of Rest Time (hours)",
    )
    # Make it dark-themed & enlarge fonts
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(size=18),
        title=dict(font=dict(size=12)),
        xaxis=dict(
            title="Rest Time (hours)",
            title_font=dict(size=12),
            tickfont=dict(size=16),
            range=[0, 48],
        ),
        yaxis=dict(
            title="Count",
            title_font=dict(size=12),
            tickfont=dict(size=16),
        ),
    )

    # ----------- 4) Fit a 2-Component Gaussian Mixture -----------
    X = hist_df["Rest Time"].values.reshape(-1, 1)
    gm = GaussianMixture(n_components=2, random_state=42)
    gm.fit(X)

    weights = gm.weights_
    means = gm.means_.flatten()
    covars = gm.covariances_.flatten()
    stdevs = np.sqrt(covars)

    # ----------- 5) Evaluate PDF (0..48) -----------
    x_vals = np.linspace(0, 48, 400)  # more points for smoother lines
    pdf_total = np.zeros_like(x_vals)
    pdf_components = []

    for w, mu, var in zip(weights, means, covars):
        sigma = np.sqrt(var)
        pdf_comp = (
            w
            * (1.0 / (sigma * np.sqrt(2.0 * np.pi)))
            * np.exp(-0.5 * ((x_vals - mu) / sigma) ** 2)
        )
        pdf_total += pdf_comp
        pdf_components.append(pdf_comp)

    # ----------- 6) Scale PDF to match histogram (counts) -----------
    bin_width = 1.0
    total_samples = len(X)
    scale_factor = total_samples * bin_width

    pdf_total_scaled = pdf_total * scale_factor
    pdf_components_scaled = [pc * scale_factor for pc in pdf_components]

    # ----------- 7) Create separate traces for each component + total -----------
    # We'll show each component with its own color, plus a sum in a different style.

    # (A) Component 1
    comp1_label = (
        f"Gaussian 1<br>"
        f"μ={means[0]:.1f}, σ={stdevs[0]:.1f}, w={weights[0]:.2f}"
    )
    trace_comp1 = go.Scatter(
        x=x_vals,
        y=pdf_components_scaled[0],
        mode="lines",
        line=dict(color="red", width=3),
        name=comp1_label,
    )

    # (B) Component 2
    comp2_label = (
        f"Gaussian 2<br>"
        f"μ={means[1]:.1f}, σ={stdevs[1]:.1f}, w={weights[1]:.2f}"
    )
    trace_comp2 = go.Scatter(
        x=x_vals,
        y=pdf_components_scaled[1],
        mode="lines",
        line=dict(color="orange", width=3),
        name=comp2_label,
    )

    # (C) Total (sum) PDF
    sum_label = "Total PDF"
    trace_sum = go.Scatter(
        x=x_vals,
        y=pdf_total_scaled,
        mode="lines",
        line=dict(color="white", width=3, dash="dash"),
        name=sum_label,
    )

    # Convert the px.histogram figure to graph_objects so we can add multiple traces
    fig = fig.update_traces(marker_color="blue")  # e.g. set histogram color
    fig.add_trace(trace_comp1)
    fig.add_trace(trace_comp2)
    fig.add_trace(trace_sum)

    # ----------- 8) Position Legend Inside Plot -----------
    fig.update_layout(
        legend=dict(
            x=0.02,    # left margin
            y=0.98,    # top margin
            xanchor="left",
            yanchor="top",
            bgcolor="rgba(0,0,0,0)",    # transparent legend
            bordercolor="white",
            borderwidth=1,
            font=dict(size=14),
        )
    )

    return fig
