import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import signal

def create_fft_analysis(df: pd.DataFrame, start_day: int = None, end_day: int = None) -> go.Figure:
    """
    Creates a figure showing the Fourier transform of effective weight lifted per day.
    This helps identify periodic patterns in lifting weights (e.g., weekly, monthly cycles).
    
    Args:
        df: DataFrame containing the lifting data
        start_day: Starting day number for analysis (inclusive)
        end_day: Ending day number for analysis (inclusive)
    """
    
    # Ensure needed columns
    needed_cols = ["Day Number", "Effective Weight"]
    for col in needed_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

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

    # Get the day numbers and weights
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
    
    # Create the figure
    fig = go.Figure()
    
    # Add the FFT magnitude trace
    fig.add_trace(go.Scatter(
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
    ))
    
    # Add markers for notable periods (weekly, biweekly, monthly)
    notable_periods = [7, 14, 30.44]  # days
    notable_labels = ['Weekly', 'Biweekly', 'Monthly']
    
    for period, label in zip(notable_periods, notable_labels):
        fig.add_vline(
            x=period,
            line_dash="dash",
            line_color="rgba(255, 255, 255, 0.3)",
            annotation_text=label,
            annotation_position="top",
            annotation=dict(font=dict(color="#FFFFFF"))
        )
    
    # Update layout
    date_range_text = f"Day {min_day} to {max_day}"
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        title=dict(
            text=f"Frequency Analysis of Lifting Patterns<br><sub>{date_range_text}</sub>",
            font=dict(size=24, color="#FFFFFF"),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=dict(
                text="Period (days)",
                font=dict(size=16, color="#FFFFFF")
            ),
            type="log",  # Use log scale for better visibility of different periods
            gridcolor="rgba(255, 255, 255, 0.1)",
            tickfont=dict(color="#FFFFFF"),
            range=[0.7, 2.5]  # log10 range covering ~5 days to ~316 days
        ),
        yaxis=dict(
            title=dict(
                text="Magnitude",
                font=dict(size=16, color="#FFFFFF")
            ),
            gridcolor="rgba(255, 255, 255, 0.1)",
            tickfont=dict(color="#FFFFFF"),
            rangemode="nonnegative"
        ),
        showlegend=False,
        margin=dict(l=60, r=20, t=80, b=60),
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.8)",
            font=dict(color="#FFFFFF")
        ),
        hovermode='x unified'
    )
    
    return fig
