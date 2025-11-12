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

        # # Plot legend bars
        # plot_legend_bars(zone_entry_stats_ax, zone_entry_stats)

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

    # Plot zone boundaries
    pitch.plot(
        [0, 52.5], [12, 12],
        color=styling.colors["primary"],
        linewidth=1,
        linestyle=":",
        ax=ax,
        zorder=1,
        alpha=0.5,
    )
    pitch.plot(
        [0, 52.5], [-12, -12],
        color=styling.colors["primary"],
        linewidth=1,
        linestyle=":",
        ax=ax,
        zorder=1,
        alpha=0.5,
    )

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

    # Plot entries
    metrics = [
        (left_total, left_color, 22.5),
        (center_total, center_color, 0),
        (right_total, right_color, -22.5),
    ]

    for total, color, x_pos in metrics:
        ax.text(
            x_pos, 8,
            f"{total}",
            fontsize=styling.typo["sizes"]["h2"],
            fontproperties=styling.fonts['medium_italic'],
            color=color,
            ha='center',
            va='bottom',
        )
        ax.text(
            x_pos, 6,
            f"entries",
            fontsize=styling.typo["sizes"]["p"],
            fontproperties=styling.fonts['medium_italic'],
            color=color,
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
        ('shot_rate', 'Shot rate', 1.1, '{:.1f}%'),
        ('xg_per_entry', 'xG per entry', 0.8, '{:.3f}'),
        ('box_entry_rate', 'Box entry rate', 0.5, '{:.1f}%'),
        ('recycle_rate', 'Recycle rate', 0.2, '{:.1f}%'),
        ('turnover_rate', 'Turnover rate', -0.1, '{:.1f}%'),
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

def plot_legend_bars(ax, zone_entry_stats):
    """
    Plot the zone entry stats as vertical bar charts.
    """
    # Turn off axis
    ax.axis('off')

    # Metrics configuration: (column_name, display_label, format_string, is_percentage, color)
    metrics = [
        ('shot_rate', 'Shot rate', '{:.1f}%', True, '#FF6B6B'),  # Red
        ('xg_per_entry', 'xG per entry', '{:.3f}', False, '#4ECDC4'),  # Teal
        ('box_entry_rate', 'Box entry rate', '{:.1f}%', True, '#95E1D3'),  # Light teal
        ('recycle_rate', 'Recycle rate', '{:.1f}%', True, '#FFE66D'),  # Yellow
        ('turnover_rate', 'Turnover rate', '{:.1f}%', True, '#A8E6CF'),  # Light green
    ]
    
    # Bar chart settings
    bar_width = 0.055
    bar_spacing = 0.18
    start_x = 0.14
    
    # Opacity settings
    base_opacity = 0.4
    max_opacity = 1.0
    
    # Zone labels - add these at the top
    zone_labels = ['Left', 'Center', 'Right']
    for j, label in enumerate(zone_labels):
        x_pos = start_x + j * 0.28 + bar_width / 2
        ax.text(
            x_pos, 1.12,
            label,
            fontsize=9,
            fontproperties=styling.fonts['medium'],
            color=styling.colors['primary'],
            ha='center',
            va='bottom',
            transform=ax.transAxes,
        )
    
    # Plot each metric
    for i, (column_name, label, fmt, is_percentage, color) in enumerate(metrics):
        y_pos = 1.0 - i * bar_spacing
        
        # Add label
        ax.text(
            0.08, y_pos,
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
        
        # For percentage metrics, normalize to 100 for bar height
        # For non-percentage (xG), we'll scale differently
        if is_percentage:
            max_val_for_scaling = 100
        else:
            max_val_for_scaling = max(zone_values.values()) * 25  # Scale xG to be visible
        
        # Add bars for each zone
        zones = ['left', 'center', 'right']
        for j, zone in enumerate(zones):
            value = zone_values[zone]
            opacity = max_opacity if zone == max_zone else base_opacity
            
            # Calculate bar height (normalized)
            if is_percentage:
                bar_height = value / max_val_for_scaling * 0.13  # Scale to visual size
            else:
                bar_height = value / max_val_for_scaling * 0.13
            
            # Calculate x position for this bar
            x_pos = start_x + j * 0.28
            
            # Draw the bar as a rectangle
            rect = Rectangle(
                (x_pos, y_pos - 0.065),  # (x, y) bottom-left corner
                bar_width,  # width
                bar_height,  # height
                facecolor=color,  # Use metric color instead of zone color
                edgecolor=None,
                alpha=opacity,
                transform=ax.transAxes
            )
            ax.add_patch(rect)
            
            # Add text value inside/on the bar
            text_y = y_pos - 0.065 + bar_height / 2
            ax.text(
                x_pos + bar_width / 2, text_y,
                fmt.format(value),
                fontsize=8,
                fontproperties=styling.fonts['medium'],
                color='white' if opacity == max_opacity else color,
                ha='center',
                va='center',
                transform=ax.transAxes,
            )