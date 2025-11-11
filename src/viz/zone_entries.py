import logging
from matplotlib.patches import Polygon
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
import numpy as np
import pandas as pd
from pathlib import Path
from matplotlib.patches import Rectangle
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
from datetime import datetime

from config import styling, PitchZones

logger = logging.getLogger(__name__)

def plot_final_third_entries(final_third_entries_df: pd.DataFrame, zone_entry_stats: pd.DataFrame, team_name: str):
    """
    Plot the final third entries and the stats per zone.

    Parameters:
    -----------
    final_third_entries_df: pd.DataFrame
        The dataframe with the zone entries data.
    zone_entry_stats: pd.DataFrame
        The dataframe with the zone entry stats.
    team_name: str
        The name of the team.
    
    Returns:
    --------
    fig: matplotlib.figure.Figure
        The figure object of the final third entries and the stats per zone.
    """

    try:
        # Init plt styling
        plt.rcParams.update({
            'font.family': styling.fonts['light'].get_name(),
            'font.size': styling.typo['sizes']['p'],
            'text.color': styling.colors['primary'],
            'axes.labelcolor': styling.colors['primary'],
            'axes.edgecolor': styling.colors['primary'],
            'xtick.color': styling.colors['primary'],
            'ytick.color': styling.colors['primary'],
            'grid.color': styling.colors['primary'],
            'figure.facecolor': styling.colors['light'],
            'axes.facecolor': styling.colors['light'],
        })

        # Create figure
        fig = plt.figure(figsize=(9, 10))
        gs = fig.add_gridspec(3, 1, hspace=0.35, wspace=0.3, 
                    height_ratios=[0.25, 1.75, 0.6])

        # Init axis
        heading_ax = fig.add_subplot(gs[0, :])
        zone_entries_ax = fig.add_subplot(gs[1, :])
        zone_entry_stats_ax = fig.add_subplot(gs[2, :])

        # Plot heading
        plot_heading(heading_ax, team_name)

        # Plot zone entries
        plot_zone_entries(zone_entries_ax, final_third_entries_df, zone_entry_stats)

        # Plot zone entry stats
        plot_zone_entry_stats(zone_entry_stats_ax, zone_entry_stats)

        # Save plot
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent
        default_kwargs = {
            'bbox_inches': 'tight',
            'pad_inches': 0.25,
            'facecolor': styling.colors['light'],
            'dpi': 300
        }
        # team name: lowercase, replace spaces with hyphens
        team_name = team_name.lower().replace(' ', '-')
        output_path = project_root / 'outputs' / 'zone_entries' / f'{team_name}-{datetime.now().strftime("%Y-%m-%d")}.png'
        fig.savefig(output_path, **default_kwargs)

        return fig

    except Exception as e:
        logger.error(f"Error plotting zone entries: {e}")
        raise e

def plot_heading(ax, team_name):
    """
    Plot the heading.
    """
    # Turn off axis
    ax.axis('off')

    # Plot heading
    ax.text(
        0, 0.25,
        f"How did we attack the low block?", 
        fontsize=styling.typo["sizes"]["h1"], 
        fontproperties=styling.fonts['medium_italic'], 
        color=styling.colors['primary'], 
        ha='left', 
        va='center',
    )

    # Plot subtitle
    ax.text(
        0, -0.3,
        f"Looking at {team_name}'s final third entries and analyzing the outcome per zone",
        fontsize=styling.typo["sizes"]["p"], 
        fontproperties=styling.fonts['light'], 
        color=styling.colors['primary'], 
        ha='left', 
        va='center',
    )

    # Belgium logo
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    logo_path = project_root / 'static' / 'bel-logo.png'
    logo = mpimg.imread(logo_path)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab_belgium_logo = AnnotationBbox(
        imagebox, 
        (0.95, 0.8),                 # location of annotation box
        xycoords='axes fraction',   # use axes fraction coordinates: relative to axes and percentage of axes for position
        box_alignment=(0.5, 1),       # alignment of the annotation box: (1, 0) means right-aligned and bottom-aligned
        frameon=False               # don't show the frame of the annotation box
    )
    ax.add_artist(ab_belgium_logo)

def plot_zone_entries(ax, final_third_entries_df, zone_entry_stats):
    """
    Plot the zone entries.
    """
    # Turn off axis
    ax.axis('off')

    # Create pitch
    pitch = VerticalPitch(
        pitch_type=styling.pitch['pitch_type'],
        pitch_length=styling.pitch['pitch_length'],
        pitch_width=styling.pitch['pitch_width'],
        line_color=styling.pitch['line_color'], 
        linewidth=styling.pitch['linewidth'], 
        goal_type=styling.pitch['goal_type'], 
        corner_arcs=styling.pitch['corner_arcs'],
        half=True,
        pad_bottom=-10,
    )
    pitch.draw(ax=ax)

    # Manually reposition the axes to move pitch up and create space below
    pos = ax.get_position()  # Get current position [left, bottom, width, height]
    # Move the axes up by reducing bottom and decreasing height
    ax.set_position([pos.x0, pos.y0 + 0.025, pos.width, pos.height])

    # Colors
    left_color = styling.colors['left_zone']
    center_color = styling.colors['center_zone']
    right_color = styling.colors['right_zone']

    # Plot zone entries
    pitch.scatter(
        final_third_entries_df['endPosXM'],
        final_third_entries_df['endPosYM'],
        c=final_third_entries_df['entry_zone'].map({
            'left': left_color,
            'center': center_color,
            'right': right_color,
        }),
        s=50,
        edgecolors=None,
        ax=ax,
        zorder=0,
        alpha=0.25,
    )

    # Plot totals
    left_total = zone_entry_stats[zone_entry_stats['entry_zone'] == 'left']['total_entries'].values[0]
    center_total = zone_entry_stats[zone_entry_stats['entry_zone'] == 'center']['total_entries'].values[0]
    right_total = zone_entry_stats[zone_entry_stats['entry_zone'] == 'right']['total_entries'].values[0]

    # Left total
    ax.text(
        22.5, 8,
        f"{left_total}",
        fontsize=styling.typo["sizes"]["h2"],
        fontproperties=styling.fonts['medium_italic'],
        color=left_color,
        ha='center',
        va='bottom',
    )
    ax.text(
        22.5, 6,
        f"entries",
        fontsize=styling.typo["sizes"]["p"],
        fontproperties=styling.fonts['medium_italic'],
        color=left_color,
        ha='center',
        va='bottom',
    )
    
    # Center total
    ax.text(
        0, 8,
        f"{center_total}",
        fontsize=styling.typo["sizes"]["h2"],
        fontproperties=styling.fonts['medium_italic'],
        color=center_color,
        ha='center',
        va='bottom',
    )
    ax.text(
        0, 6,
        f"entries",
        fontsize=styling.typo["sizes"]["p"],
        fontproperties=styling.fonts['medium_italic'],
        color=center_color,
        ha='center',
        va='bottom',
    )
    
    # Right total
    ax.text(
        -22.5, 8,
        f"{right_total}",
        fontsize=styling.typo["sizes"]["h2"],
        fontproperties=styling.fonts['medium_italic'],
        color=right_color,
        ha='center',
        va='bottom',
    )
    ax.text(
        -22.5, 6,
        f"entries",
        fontsize=styling.typo["sizes"]["p"],
        fontproperties=styling.fonts['medium_italic'],
        color=right_color,
        ha='center',
        va='bottom',
    )

def plot_zone_entry_stats(ax, zone_entry_stats):
    """
    Plot the zone entry stats.
    """
    # Turn off axis
    ax.axis('off')

    # Colors
    zone_colors = {
        'left': styling.colors['left_zone'],
        'center': styling.colors['center_zone'],
        'right': styling.colors['right_zone']
    }

    # Zone x-positions
    zone_x_positions = {
        'left': 0.21,
        'center': 0.5,
        'right': 0.795,
    }
    
    # Metrics configuration: (column_name, display_label, y_position, format_string)
    metrics = [
        ('shot_rate', 'Shot rate', 1.1, '{:.2f}%'),
        ('xg_per_entry', 'xG per entry', 0.8, '{:.3f}'),
        ('box_entry_rate', 'Box entry rate', 0.5, '{:.2f}%'),
        ('recycle_rate', 'Recycle rate', 0.2, '{:.2f}%'),
        ('turnover_rate', 'Turnover rate', -0.1, '{:.2f}%'),
    ]
    
    # Opacity settings
    base_opacity = 0.3
    max_opacity = 1.0
    
    # Plot each metric
    for column_name, label, y_pos, fmt in metrics:
        # Add label
        ax.text(
            0.1, y_pos,
            label,
            fontsize=10,
            fontproperties=styling.fonts['light'],
            color=styling.colors['primary'],
            ha='right',
            va='center',
        )
        
        # Get values for all zones
        zone_values = {
            zone: zone_entry_stats[zone_entry_stats['entry_zone'] == zone][column_name].values[0]
            for zone in ['left', 'center', 'right']
        }
        
        # Find the zone with the maximum value
        max_zone = max(zone_values, key=zone_values.get)
        
        # Add values for each zone with appropriate opacity
        for zone in ['left', 'center', 'right']:
            value = zone_values[zone]
            opacity = max_opacity if zone == max_zone else base_opacity
            
            ax.text(
                zone_x_positions[zone], y_pos,
                fmt.format(value),
                fontsize=styling.typo["sizes"]["p"],
                fontproperties=styling.fonts['medium_italic'],
                color=zone_colors[zone],
                alpha=opacity,
                ha='center',
                va='center',
            )