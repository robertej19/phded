import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.lines import Line2D
# Sample data
planets = [
    {'name': 'Mercury', 'distance': 0.39, 'moons': 1, 'mass': 0.055, 'rotational_speed': 10.89, 'type': 'rocky'},
    {'name': 'Venus', 'distance': 0.72, 'moons': 1, 'mass': 0.815, 'rotational_speed': -6.52, 'type': 'rocky'},
    {'name': 'Earth', 'distance': 1.00, 'moons': 2, 'mass': 1.0, 'rotational_speed': 1.00, 'type': 'rocky'},
    {'name': 'Mars', 'distance': 1.52, 'moons': 4, 'mass': 0.107, 'rotational_speed': 0.97, 'type': 'rocky'},
    {'name': 'Jupiter', 'distance': 5.20, 'moons': 79, 'mass': 317.8, 'rotational_speed': 12.6, 'type': 'gas giant'},
    {'name': 'Saturn', 'distance': 9.58, 'moons': 82, 'mass': 95.2, 'rotational_speed': 9.7, 'type': 'gas giant'},
    {'name': 'Uranus', 'distance': 19.20, 'moons': 27, 'mass': 14.5, 'rotational_speed': -6.8, 'type': 'gas giant'},
    {'name': 'Neptune', 'distance': 30.05, 'moons': 44, 'mass': 17.1, 'rotational_speed': 5.4, 'type': 'gas giant'},
    {'name': 'Pluto', 'distance': 39.48, 'moons': 15, 'mass': 0.00218, 'rotational_speed': -6.39, 'type': 'rocky'},
]

# Extract data for plotting
distance = np.array([planet['distance'] for planet in planets])
moons = np.array([planet['moons'] for planet in planets])
mass = np.array([planet['mass'] for planet in planets])
rot_speed = np.array([abs(planet['rotational_speed']) for planet in planets])  # Use absolute values for rotational speed
types = [planet['type'] for planet in planets]
names = [planet['name'] for planet in planets]

# Determine markers based on planet type
marker_dict = {'rocky': 'o', 'gas giant': '*'}

# Compute logarithmic scaling for marker sizes
# Avoid log(0) by ensuring mass > 0
min_mass = mass.min()
log_mass = np.sqrt((mass / min_mass)**1)  # Relative to the smallest mass
mass_scaled = log_mass * 100 + 20  # Scale factor adjusted for better visibility

# Handle zero moons by replacing with a small positive number for log scale
# Alternatively, exclude planets with zero moons or adjust the y-axis labels
# Here, we'll replace zero with a small value (e.g., 0.1)
moons = np.where(moons == 0, 0.1, moons)

# Normalize rotational speeds for colormap
norm = Normalize(vmin=rot_speed.min(), vmax=rot_speed.max())

# Create a figure and axis
fig, ax = plt.subplots(figsize=(12, 8))
#increase font size to 24 everywhere
plt.rcParams.update({
    'font.size': 28,
})

heights = [0.2,0.2,0.5,1,100,80,10,20,2]
# Plot planets grouped by type
for planet_type, marker in marker_dict.items():
    indices = [i for i, t in enumerate(types) if t == planet_type]
    scatter = ax.scatter(
        distance[indices],
        moons[indices],
        s=mass_scaled[indices],
        c=rot_speed[indices],
        cmap='viridis',
        norm=norm,
        alpha=0.7,
        edgecolors='w',
        linewidth=0.5,
        marker=marker,
        label=planet_type.capitalize()
    )
    # Add labels for each planet
    for i in indices:
        ax.text(
            distance[i],
            moons[i] + heights[i],  # Offset label slightly above marker
            names[i],
            ha='center',
            fontsize=28
        )

# Add a colorbar and link it to the scatter plot
cbar = fig.colorbar(scatter, ax=ax)
cbar.set_label('Rotational Speed (Earth days)')#, fontsize=14)

# Customize plot
ax.set_xlabel('Distance from Earth (AU)', fontsize=28)
ax.set_ylabel('Number of Moons', fontsize=28)
ax.set_yscale("log")
ax.set_xscale("log")
ax.set_ylim([0.7,300])
ax.set_xlim([0.2,50])


ax.set_title('Planets: Distance, Speed, Size, # of Moons, and Type', fontsize=28)
#ax.grid(True, linestyle='--', alpha=0.6)
# Create a custom legend with uniform marker sizes
legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='Rocky',
           markerfacecolor='black', markersize=30, markeredgewidth=0.5),
    Line2D([0], [0], marker='*', color='w', label='Gas Giant',
           markerfacecolor='black', markersize=30, markeredgewidth=0.5)
]
ax.legend(handles=legend_elements, title='Planet Type', fontsize=24,loc='upper left')


#ax.legend(title='Planet Type', fontsize=24,loc='upper left')
# Adjust tick label size for x and y axes
ax.tick_params(axis='both', which='major', labelsize=28)  # For major ticks
ax.tick_params(axis='both', which='minor', labelsize=28)  # For minor ticks

# Show the plot
plt.tight_layout()
plt.show()
