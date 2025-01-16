# charts/boolean_grip_heatmap.py

import pandas as pd
import plotly.graph_objects as go

def create_boolean_grip_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    Creates a 2D heatmap where:
    - The x-axis represents combinations of 'Grip', 'Beltless', and 'Stiff Bar'.
    - The y-axis represents combinations of 'Deficiet' and 'Pauses'.
    - The z-values represent the count of occurrences for each combination.

    Zero values are displayed as white.
    """

    # Ensure required columns exist
    required_cols = ["Grip", "Beltless", "Stiff Bar", "Deficiet", "Pauses"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Convert boolean columns to strings for easier concatenation
    df["Beltless"] = df["Beltless"].astype(str)
    df["Stiff Bar"] = df["Stiff Bar"].astype(str)
    df["Deficiet"] = df["Deficiet"].astype(str)
    df["Pauses"] = df["Pauses"].astype(str)

    # Create combinations for x-axis and y-axis
    df["X_Combination"] = (
        df["Grip"] + 
        "-Beltless-" + df["Beltless"] + 
        "-StiffBar-" + df["Stiff Bar"]
    )
    df["Y_Combination"] = (
        "Deficiet-" + df["Deficiet"] +
        "-Pauses-" + df["Pauses"]
    )

    # Count occurrences for each combination
    heatmap_data = df.groupby(["X_Combination", "Y_Combination"]).size().reset_index(name="Count")

    # Pivot data for heatmap
    pivot_table = heatmap_data.pivot(index="Y_Combination", columns="X_Combination", values="Count").fillna(0)

    # Convert pivot table to numpy array for z-values
    z_values = pivot_table.values

    # Define a custom colorscale with white for zero values
    colorscale = [
        [0.0, "white"],  # Map zero values to white
        [0.01, "rgb(68, 1, 84)"],  # Start Viridis scale after zero
        [1.0, "rgb(253, 231, 37)"]
    ]

    # Create heatmap
    fig = go.Figure(
        data=go.Heatmap(
            z=z_values,
            x=pivot_table.columns,
            y=pivot_table.index,
            colorscale=colorscale,
            colorbar=dict(title="Count"),
            zmin=0,  # Ensure valid range for colormap
            zmax=z_values.max()
        )
    )

    # Update layout
    fig.update_layout(
        title="2D Heatmap of Grip and Boolean Combinations",
        xaxis=dict(title="Grip and Beltless/Stiff Bar Combinations", tickangle=45),
        yaxis=dict(title="Deficiet and Pauses Combinations"),
        #template="plotly_white"
        template="plotly_dark",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",

    )

    return fig
