import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import plotly.colors

def create_color_coded_histogram(df):
    """
    Create a color-coded histogram where each day's Top Set weight is represented as a bar,
    with color from viridis colormap indicating how long ago the lift occurred.
    Visualized like a Tetris game with weight on x-axis and stacked unit blocks.
    """
    # Sort the dataframe by Top Set weight for proper stacking
    df = df.sort_values('Top Set Weight')
    
    # Convert YYYYMMDD integer dates to datetime objects
    dates = [datetime.strptime(str(date), '%Y%m%d').date() for date in df['Date']]
    
    # Calculate days ago for each entry
    latest_date = datetime.now().date()
    days_ago = [(latest_date - date).days for date in dates]
    
    # Calculate color ratios (days_ago / max_days) and invert them
    max_days = max(days_ago)
    color_ratios = [1 - (d/max_days) for d in days_ago]  # Invert the ratio
    
    # Create a continuous color scale from viridis
    colors = [
        plotly.colors.sample_colorscale(
            'Viridis', 
            ratio, 
            colortype='rgb'
        )[0] for ratio in color_ratios
    ]
    
    # Group by Top Set weight to determine stacking
    weight_counts = df['Top Set Weight'].value_counts().sort_index()
    
    # Create arrays for stacked bars
    weights = []
    y_positions = []
    dates_list = []
    days_ago_list = []
    ratios_list = []
    colors_list = []
    reps_list = []
    
    # For each unique weight, create stacked unit bars
    for weight, count in weight_counts.items():
        # Find all entries with this weight
        mask = df['Top Set Weight'] == weight
        weight_dates = [d for d, m in zip(dates, mask) if m]
        weight_days_ago = [d for d, m in zip(days_ago, mask) if m]
        weight_ratios = [r for r, m in zip(color_ratios, mask) if m]
        weight_colors = [c for c, m in zip(colors, mask) if m]
        weight_reps = [r for r, m in zip(df['Number of Reps'], mask) if m]
        
        # Add a unit bar for each occurrence
        for i in range(count):
            weights.append(weight)
            y_positions.append(1)  # Stack from bottom up
            dates_list.append(weight_dates[i])
            days_ago_list.append(weight_days_ago[i])
            ratios_list.append(weight_ratios[i])
            colors_list.append(weight_colors[i])
            reps_list.append(weight_reps[i])
    
    # Create the figure
    fig = go.Figure()
    
    # Add bars for each day's Top Set weight
    fig.add_trace(
        go.Bar(
            x=weights,
            y=y_positions,
            customdata=list(zip(dates_list, days_ago_list, ratios_list, reps_list)),
            marker=dict(
                color=colors_list,
                line=dict(
                    color=colors_list,
                    width=1
                ),
                colorbar=dict(
                    title='Days Ago Ratio',
                    titleside='right',
                    tickformat='.2%'  # Format as percentage
                ),
                colorscale='Viridis'
            ),
            hovertemplate=(
                'Top Set Weight: %{x:.0f} lbs<br>'
                'Reps: %{customdata[3]:.0f}<br>'
                'Date: %{customdata[0]}<br>'
                'Days Ago: %{customdata[1]:.0f}<br>'
                'Time Ratio: %{customdata[2]:.1%}<br>'
                '<extra></extra>'
            ),
            width=5  # Make bars thinner for better visualization
        )
    )
    
    fig.update_layout(
        title=dict(
            text='Top Set Weight Distribution (Color by Days Ago)',
            x=0.5,
            xanchor='center'
        ),
        xaxis_title='Top Set Weight (lbs)',
        yaxis_title='Count',
        font=dict(
            family="Arial, sans-serif",
            size=18,
            color="#FFFFFF"
        ),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
        showlegend=False,
        bargap=0,  # Remove gaps between bars
        bargroupgap=0  # Remove gaps between bar groups
    )
    
    # Update axes formatting
    fig.update_xaxes(
        title_font=dict(size=20, color="#FFFFFF"),
        tickfont=dict(size=16, color="#FFFFFF")
    )
    fig.update_yaxes(
        title_font=dict(size=20, color="#FFFFFF"),
        tickfont=dict(size=16, color="#FFFFFF")
    )
    
    return fig
