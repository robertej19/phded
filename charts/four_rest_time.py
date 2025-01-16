# charts/rest_time_hist.py

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.mixture import GaussianMixture

def create_rest_time_histogram(df: pd.DataFrame):
    """
    1) Computes a new column 'Rest Time' in hours, representing the time between
       consecutive lifts on consecutive days:
         Rest Time (day i) = 24 - (DecimalHour of day i-1) + (DecimalHour of day i)
       if day i is exactly day_number(previous) + 1.
    2) Creates a histogram of 'Rest Time' with font sizes increased.
    3) Fits a 2-component Gaussian Mixture Model to 'Rest Time' and overlays
       its bimodal PDF on top of the histogram.

    Requirements:
      - The DataFrame has columns: "Day Number" (int) and "DecimalHour" (float).
      - The data must be sorted or can be sorted here to align consecutive days.
    """

    # Ensure needed columns exist
    required_cols = {"Day Number", "DecimalHour"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"DataFrame must contain {required_cols} columns.")

    # Sort by Day Number (and maybe DecimalHour if multiple lifts per day)
    df = df.sort_values(["Day Number", "DecimalHour"]).reset_index(drop=True)

    # Create a new column 'Rest Time' initialized to NaN
    df["Rest Time"] = np.nan

    # Iterate through rows to calculate consecutive rest times
    for i in range(1, len(df)):
        curr_day = df.loc[i, "Day Number"]
        prev_day = df.loc[i - 1, "Day Number"]

        curr_dec_hour = df.loc[i, "DecimalHour"]
        prev_dec_hour = df.loc[i - 1, "DecimalHour"]

        # If days are consecutive (e.g., day 10 => day 11)
        if curr_day == prev_day + 1:
            df.loc[i, "Rest Time"] = 24 - prev_dec_hour + curr_dec_hour

    # Build a histogram of 'Rest Time'
    # Drop any NaN since not all rows will have a rest time
    hist_df = df.dropna(subset=["Rest Time"])

    # Create the basic histogram using Plotly Express
    fig = px.histogram(
        hist_df,
        x="Rest Time",
        nbins=48,
        title="Histogram of Rest Time (hours)",
    )

    # ----------------------------
    # 1) Increase Font Everywhere
    # ----------------------------
    fig.update_layout(
        template="plotly_white",
        font=dict(size=18),  # Global font size
        title=dict(font=dict(size=24)),
        xaxis=dict(
            title="Rest Time (hours)",
            title_font=dict(size=20),
            tickfont=dict(size=16),
        ),
        yaxis=dict(
            title="Count",
            title_font=dict(size=20),
            tickfont=dict(size=16),
        ),
    )

    # --------------------------------------------------
    # 2) Fit a 2-Component Gaussian Mixture to Rest Time
    # --------------------------------------------------
    X = hist_df["Rest Time"].dropna().values.reshape(-1, 1)

    # Fit a 2-component (bimodal) Gaussian mixture
    gm = GaussianMixture(n_components=2, random_state=42)
    gm.fit(X)

    # Extract mixture parameters
    weights = gm.weights_
    means = gm.means_.flatten()
    covars = gm.covariances_.flatten()  # each is variance for 1D

    # Build an x-grid to evaluate the PDF
    x_min, x_max = X.min(), X.max()
    x_vals = np.linspace(x_min, x_max, 200).reshape(-1, 1)

    # Evaluate PDF = sum of (weight_i * Normal(mean_i, var_i).pdf(x_vals))
    pdf = np.zeros_like(x_vals.flatten())
    for w, mu, var in zip(weights, means, covars):
        sigma = np.sqrt(var)
        component_pdf = (
            w
            * (1.0 / (sigma * np.sqrt(2.0 * np.pi)))
            * np.exp(-0.5 * ((x_vals.flatten() - mu) / sigma) ** 2)
        )
        pdf += component_pdf

    # The histogram y-axis is "count" not "density," so we need to scale the PDF to match.
    # total_area = bin_width * number_of_samples
    # We'll approximate the bin_width from histogram (range / nbins).
    range_width = x_max - x_min
    nbins = 48
    bin_width = range_width / nbins
    total_samples = len(X)
    # Scale factor = total_samples * bin_width, so the integral of pdf matches total_samples
    pdf_scaled = pdf * (total_samples * bin_width)

    # -----------------------------
    # 3) Overlay the PDF on the Plot
    # -----------------------------
    pdf_trace = go.Scatter(
        x=x_vals.flatten(),
        y=pdf_scaled,
        mode="lines",
        line=dict(color="red", width=3),
        name="Bimodal Fit",
    )

    # Convert the Plotly Express figure to a graph_objects figure so we can add a trace
    fig = fig.update_traces(marker_color="blue")  # e.g., set histogram color
    fig.add_trace(pdf_trace)

    return fig
