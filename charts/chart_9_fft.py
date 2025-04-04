import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import signal
from plotly.subplots import make_subplots

def create_fft_analysis(df: pd.DataFrame, start_day: int = None, end_day: int = None) -> go.Figure:
    """
    Creates a figure showing:
    1. Top subplot: Full time series of top set weight with shaded selected region
    2. Bottom subplot: Fourier transform of effective weight lifted per day for selected region
    
    Args:
        df: DataFrame containing the lifting data
        start_day: Starting day number for analysis (inclusive)
        end_day: Ending day number for analysis (inclusive)
    """
    
    # Ensure needed columns
    needed_cols = ["Day Number", "Effective Weight", "Top Set Weight"]
    for col in needed_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Store the full dataset
    df_full = df.copy()
    
    # Filter data by day range if specified
    if start_day is not None and end_day is not None:
        df = df[(df["Day Number"] >= start_day) & (df["Day Number"] <= end_day)].copy()

    if len(df) < 2:
        # Return an empty figure with a message if not enough data
        fig = go.Figure()
        fig.add_annotation(
            text="Not enough data points in selected range",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20, color="#FFFFFF")
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0, 0, 0, 0)",
            plot_bgcolor="rgba(0, 0, 0, 0)"
        )
        return fig

    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=["Top Set Weight Over Time (Shaded Region = FFT Analysis Range)", "Frequency Analysis"],
        vertical_spacing=0.15,
        row_heights=[0.4, 0.6]
    )

    # Add full time series of top set weight
    fig.add_trace(
        go.Scatter(
            x=df_full["Day Number"],
            y=df_full["Top Set Weight"],
            mode='lines+markers',
            name='Top Set Weight',
            line=dict(color='#3498db', width=2),
            marker=dict(size=6),
            hovertemplate=(
                "Day: %{x}<br>"
                "Weight: %{y} lbs<br>"
                "<extra></extra>"
            )
        ),
        row=1, col=1
    )

    # Add shaded region for selected range
    if start_day is not None and end_day is not None:
        fig.add_trace(
            go.Scatter(
                x=[start_day, start_day, end_day, end_day],
                y=[df_full["Top Set Weight"].min(), df_full["Top Set Weight"].max(),
                   df_full["Top Set Weight"].max(), df_full["Top Set Weight"].min()],
                fill="toself",
                fillcolor="rgba(255, 255, 255, 0.1)",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip"
            ),
            row=1, col=1
        )

    # Get the day numbers and weights for FFT
    days = df["Day Number"].values
    weights = df["Effective Weight"].values

    # Create a regular time series by interpolating missing days
    max_day = int(days.max())
    min_day = int(days.min())
    regular_days = np.arange(min_day, max_day + 1)
    
    # Interpolate weights for missing days
    interpolated_weights = np.interp(regular_days, days, weights)
    
    # Detrend the data to remove the overall increasing/decreasing trend
    detrended_weights = signal.detrend(interpolated_weights)
    
    # Apply a Hanning window to reduce spectral leakage
    window = signal.windows.hann(len(detrended_weights))
    windowed_weights = detrended_weights * window
    
    # Compute FFT
    fft_result = np.fft.rfft(windowed_weights)
    fft_freqs = np.fft.rfftfreq(len(regular_days))
    
    # Convert frequencies to periods (in days)
    periods = 1 / fft_freqs[1:]  # Skip the DC component (frequency = 0)
    magnitudes = np.abs(fft_result)[1:]  # Skip the DC component
    
    # Add the FFT magnitude trace
    fig.add_trace(
        go.Scatter(
            x=periods,
            y=magnitudes,
            mode='lines',
            name='FFT Magnitude',
            line=dict(color='#2ecc71', width=2),
            hovertemplate=(
                "Period: %{x:.1f} days<br>"
                "Magnitude: %{y:.1f}<br>"
                "<extra></extra>"
            )
        ),
        row=2, col=1
    )
    
    # Add markers for notable periods (weekly, biweekly, monthly, quarterly, semi-annual)
    notable_periods = [7, 14, 30.44, 91.31, 182.62]  # days
    notable_labels = ['Weekly', 'Biweekly', 'Monthly', 'Quarterly', 'Semi-annual']
    
    for period, label in zip(notable_periods, notable_labels):
        fig.add_vline(
            x=period,
            line_dash="dash",
            line_color="rgba(255, 255, 255, 0.3)",
            annotation_text=label,
            annotation_position="top",
            annotation=dict(font=dict(color="#FFFFFF")),
            row=2, col=1
        )
    
    # Update layout
    date_range_text = f"FFT Analysis Range: Day {min_day} to {max_day}"
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        title=dict(
            text=f"Lifting Pattern Analysis<br><sub>{date_range_text}</sub>",
            font=dict(size=24, color="#FFFFFF"),
            x=0.5,
            xanchor='center',
            y=0.95  # Move title up to create more space
        ),
        showlegend=False,
        height=400,  # Decrease overall height
        margin=dict(l=60, r=20, t=120, b=60),  # Increase top margin for title spacing
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.8)",
            font=dict(color="#FFFFFF")
        ),
        hovermode='x unified'
    )

    # Update axes
    fig.update_xaxes(
        title_text="Day Number",
        gridcolor="rgba(255, 255, 255, 0.1)",
        tickfont=dict(color="#FFFFFF"),
        title_font=dict(size=14, color="#FFFFFF"),
        row=1, col=1
    )
    
    fig.update_yaxes(
        title_text="Weight (lbs)",
        gridcolor="rgba(255, 255, 255, 0.1)",
        tickfont=dict(color="#FFFFFF"),
        title_font=dict(size=14, color="#FFFFFF"),
        row=1, col=1
    )

    fig.update_xaxes(
        title_text="Period (days)",
        type="log",
        gridcolor="rgba(255, 255, 255, 0.1)",
        tickfont=dict(color="#FFFFFF"),
        title_font=dict(size=14, color="#FFFFFF"),
        range=[0.7, np.log10(400)],  # log10 range covering ~5 days to 400 days
        row=2, col=1
    )
    
    fig.update_yaxes(
        title_text="Magnitude",
        gridcolor="rgba(255, 255, 255, 0.1)",
        tickfont=dict(color="#FFFFFF"),
        title_font=dict(size=14, color="#FFFFFF"),
        rangemode="nonnegative",
        row=2, col=1
    )

    # Update subplot titles color
    for annotation in fig.layout.annotations[:2]:  # Only update the subplot titles
        annotation.update(font=dict(color="#FFFFFF", size=16))
    
    return fig
