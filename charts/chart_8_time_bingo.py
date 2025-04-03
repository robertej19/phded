import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import scipy.stats as stats
from sklearn.mixture import GaussianMixture

def create_time_bingo(df: pd.DataFrame):
    # Compute hour and minute values from the DecimalHour column.
    df["Hour"] = df["DecimalHour"].astype(int)
    df["Minute"] = ((df["DecimalHour"] - df["Hour"]) * 60).round().astype(int)

    # ------------------------------
    # Group by Hour and Minute to Count Occurrences
    # ------------------------------
    grouped = df.groupby(['Hour', 'Minute']).size()
    # Create a 24×60 DataFrame (rows: hours 0–23, columns: minutes 0–59).
    heatmap_data = grouped.unstack(level='Minute').reindex(index=range(24), columns=range(60))
    heatmap_data = heatmap_data.fillna(0)  # replace NaN with 0

    # --------------------------------
    # Additional Calculations for Title
    # --------------------------------
    total_possible = 24 * 60  # 1440 possible unique hour-minute cells.
    non_zero_count = np.sum(heatmap_data.values != 0)
    total_entries = len(df)
    unique_hours = df['Hour'].nunique()
    unique_minutes = df['Minute'].nunique()

    # --------------------------------
    # Marginal Histograms Data
    # --------------------------------
    minute_totals = heatmap_data.sum(axis=0)  # Sum over hours (for each minute)
    hour_totals   = heatmap_data.sum(axis=1)  # Sum over minutes (for each hour)

    # --------------------------------
    # Evaluate Uniformity of Minute Data with Chi-Square Test
    # --------------------------------
    observed_minutes = minute_totals.values
    expected_minutes = np.full_like(observed_minutes, fill_value=observed_minutes.sum() / len(observed_minutes))
    minutes_chi2, minutes_p = stats.chisquare(f_obs=observed_minutes, f_exp=expected_minutes)

    # --------------------------------
    # Evaluate Uniformity of Hours Data with Chi-Square Test
    # --------------------------------
    observed_hours = hour_totals.values
    expected_hours_uniform = np.full_like(observed_hours, fill_value=observed_hours.sum() / len(observed_hours))
    hours_uniform_chi2, hours_uniform_p = stats.chisquare(f_obs=observed_hours, f_exp=expected_hours_uniform)

    # --------------------------------
    # Evaluate Hours Data against a Gaussian Distribution
    # --------------------------------
    mu = df["Hour"].mean()
    sigma = df["Hour"].std(ddof=1)
    N_hours = observed_hours.sum()
    expected_hours_gaussian = np.array([
        N_hours * (stats.norm.cdf(i + 0.5, loc=mu, scale=sigma) - stats.norm.cdf(i - 0.5, loc=mu, scale=sigma))
        for i in range(24)
    ])
    expected_hours_gaussian *= N_hours / expected_hours_gaussian.sum()
    hours_gaussian_chi2, hours_gaussian_p = stats.chisquare(f_obs=observed_hours, f_exp=expected_hours_gaussian)

    # --------------------------------
    # Evaluate Multimodality of Hours Data using a Gaussian Mixture Model
    # --------------------------------
    # Use the raw Hour values (each occurrence) for the GMM.
    hour_data = df["Hour"].values.reshape(-1, 1)
    bic_values = {}
    gmm_models = {}
    max_components = 5  # Test models with 1 to 5 components.
    for n in range(1, max_components + 1):
        gmm = GaussianMixture(n_components=n, random_state=0)
        gmm.fit(hour_data)
        bic = gmm.bic(hour_data)
        bic_values[n] = bic
        gmm_models[n] = gmm

    best_n = min(bic_values, key=bic_values.get)
    best_gmm = gmm_models[best_n]
    peaks = np.sort(best_gmm.means_.flatten())

    # Compute delta BIC values relative to the best model.
    delta_bic = {n: bic_values[n] - bic_values[best_n] for n in bic_values}

    # Pack the statistical results into a dictionary.
    stat_results = {
        "minutes_uniform": {"chi2": minutes_chi2, "p_value": minutes_p},
        "hours_uniform": {"chi2": hours_uniform_chi2, "p_value": hours_uniform_p},
        "hours_gaussian": {"chi2": hours_gaussian_chi2, "p_value": hours_gaussian_p},
        "hours_multimodal": {
            "n_components_tested": list(range(1, max_components+1)),
            "bic_values": bic_values,
            "delta_bic": delta_bic,
            "best_n_components": best_n,
            "peaks": peaks.tolist(),
        }
    }

    # --------------------------------
    # Custom Hover Text for the Main Heatmap
    # --------------------------------
    hover_text = []
    for hour in heatmap_data.index:
        row_text = []
        for minute in heatmap_data.columns:
            count = heatmap_data.loc[hour, minute]
            if count == 0:
                row_text.append("")
            else:
                row_text.append(f"Time: {hour:02d}:{minute:02d}<br>Lifts: {int(count)}")
        hover_text.append(row_text)

    # --------------------------------
    # Create the Figure with Marginals on Left and Bottom
    # --------------------------------
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "bar"}, {"type": "heatmap"}],
               [None, {"type": "bar"}]],
        shared_yaxes=True,
        shared_xaxes=True,
        row_heights=[0.8, 0.2],
        column_widths=[0.1, 0.9],
        horizontal_spacing=0.02,
        vertical_spacing=0.02
    )

    dark_colormap = 'viridis'
    # --------------------------------
    # Add the Main Heatmap (Row 1, Col 2)
    # --------------------------------
    heatmap_trace = go.Heatmap(
        z=heatmap_data.values,
        x=list(heatmap_data.columns),  # Minutes (0–59)
        y=list(heatmap_data.index),    # Hours (0–23)
        colorscale=dark_colormap,
        text=hover_text,
        hovertemplate="%{text}<extra></extra>",
        showscale=False
    )
    fig.add_trace(heatmap_trace, row=1, col=2)

    # --------------------------------
    # Add the Left Marginal: Hour Distribution (Row 1, Col 1)
    # --------------------------------
    hour_bar = go.Bar(
        x=hour_totals.values,
        y=list(heatmap_data.index),
        orientation='h',
        marker_color='gray',
        showlegend=False,
        hovertemplate="Hour: %{y}<br>Lifts: %{x}<extra></extra>"
    )
    fig.add_trace(hour_bar, row=1, col=1)

    # --------------------------------
    # Overlay GMM Curves on the Hour Distribution
    # --------------------------------
    # Create a fine grid for hour values.
    x_hours = np.linspace(0, 23, 240)  # Fine grid (0.1 increments)
    composite_curve = np.zeros_like(x_hours)
    for k in range(best_n):
        weight = best_gmm.weights_[k]
        mu_k = best_gmm.means_[k, 0]
        sigma_k = np.sqrt(best_gmm.covariances_[k].squeeze())
        # Compute the PDF for this component, scaled by total counts (bin width = 1)
        component_curve = weight * stats.norm.pdf(x_hours, loc=mu_k, scale=sigma_k) * N_hours
        composite_curve += component_curve
        # Add individual component trace (dashed line)
        comp_trace = go.Scatter(
            x=component_curve,
            y=x_hours,
            mode='lines',
            line=dict(dash='dash', width=2),
            name=f'Component {k+1}',
            showlegend=False,
            hoverinfo='skip'
        )
        fig.add_trace(comp_trace, row=1, col=1)
    # Add composite GMM curve (solid line)
    composite_trace = go.Scatter(
        x=composite_curve,
        y=x_hours,
        mode='lines',
        line=dict(color='cyan', width=2),
        name='GMM Total',
        showlegend=False,
        hoverinfo='skip'
    )
    fig.add_trace(composite_trace, row=1, col=1)

    # --------------------------------
    # Add the Bottom Marginal: Minute Distribution (Row 2, Col 2)
    # --------------------------------
    minute_bar = go.Bar(
        x=list(heatmap_data.columns),
        y=minute_totals.values,
        marker_color='gray',
        showlegend=False,
        hovertemplate="Minute: %{x}<br>Lifts: %{y}<extra></extra>"
    )
    fig.add_trace(minute_bar, row=2, col=2)
    
    fig.update_xaxes(title_text="Minute of Hour", row=2, col=2)
    fig.update_yaxes(title_text="Hour of Day", row=1, col=1)
    fig.update_xaxes(autorange='reversed', row=1, col=1)
    fig.update_yaxes(autorange='reversed', row=2, col=2)
    fig.update_xaxes(showticklabels=False, row=1, col=1)
    fig.update_yaxes(showticklabels=False, row=2, col=2)
    fig.update_yaxes(showgrid=False, row=2, col=2)
    fig.update_xaxes(showgrid=False, row=1, col=1)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        autosize=True,
        font=dict(
            family="Arial, sans-serif",
            size=16,
            color="#FFFFFF"
        ),
        title=dict(
            text=f"Bingo Chart of Lift Clock Times:<br>{non_zero_count}/{total_possible} Times Recorded",
            font=dict(
                size=28,
                color="#FFFFFF"
            ),
            x=0.5
        ),
        margin=dict(l=60, r=60, t=100, b=60)
    )

    return fig, stat_results
