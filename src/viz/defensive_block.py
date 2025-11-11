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

def plot_defensive_blocks(block_analysis: dict, defending_team_name: str, attacking_team_name: str):
    """
    Plot the defensive blocks depending on the ball position (grouped by zone).

    Parameters:
    -----------
    block_analysis: dict
        The block analysis dictionary.
    defending_team_name: str
        The name of the defending team.
    attacking_team_name: str
        The name of the attacking team.

    Returns:
    --------
    fig: matplotlib.figure.Figure
        The figure object of the defensive blocks.
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
        fig = plt.figure(figsize=(11, 9))
        gs = fig.add_gridspec(4, 3, hspace=0.35, wspace=0.3, 
                    height_ratios=[0.5, 1, 0.1, 1], width_ratios=[1, 1, 1])
        
        # Init axis
        heading_ax = fig.add_subplot(gs[0, :])
        block_left_final_third_ax = fig.add_subplot(gs[1, 0])
        block_center_final_third_ax = fig.add_subplot(gs[1, 1])
        block_right_final_third_ax = fig.add_subplot(gs[1, 2])
        spacer_ax = fig.add_subplot(gs[2, :])
        block_left_prog_zone_ax = fig.add_subplot(gs[3, 0])
        block_center_prog_zone_ax = fig.add_subplot(gs[3, 1])
        block_right_prog_zone_ax = fig.add_subplot(gs[3, 2])

        # Plot heading
        plot_heading(heading_ax, defending_team_name, attacking_team_name)

        spacer_ax.axis('off')

        # Plot blocks by zone
        plot_blocks_by_zone(block_left_final_third_ax, block_analysis["left_final_third"], "left_final_third")
        plot_blocks_by_zone(block_center_final_third_ax, block_analysis["center_final_third"], "center_final_third")
        plot_blocks_by_zone(block_right_final_third_ax, block_analysis["right_final_third"], "right_final_third")
        plot_blocks_by_zone(block_left_prog_zone_ax, block_analysis["left_progression"], "left_progression")
        plot_blocks_by_zone(block_center_prog_zone_ax, block_analysis["center_progression"], "center_progression")
        plot_blocks_by_zone(block_right_prog_zone_ax, block_analysis["right_progression"], "right_progression")

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
        defending_team_name = defending_team_name.lower().replace(' ', '-')
        output_path = project_root / 'outputs' / 'defensive_block' / f'{defending_team_name}-{datetime.now().strftime("%Y-%m-%d")}.png'
        fig.savefig(output_path, **default_kwargs)

        return fig

        # return fig
    
    except Exception as e:
        logger.error(f"Error plotting defensive blocks: {e}")
        return None

def plot_heading(ax, defending_team_name, attacking_team_name):
    """
    Plot the heading.
    """
    # Turn off axis
    ax.axis('off')

    # Get team colors from styling
    # color = styling.colors[defending_team_name]

    # Plot heading
    ax.text(
        0.5, 0.5,
        f"{defending_team_name}'s low block organization", 
        fontsize=styling.typo["sizes"]["h1"], 
        fontproperties=styling.fonts['medium_italic'], 
        color=styling.colors['primary'], 
        ha='center', 
        va='center',
    )

    # Plot subtitle
    ax.text(
        0.5, 0.05,
        f"Depending on {attacking_team_name}'s different possession zones",
        fontsize=styling.typo["sizes"]["p"], 
        fontproperties=styling.fonts['light'], 
        color=styling.colors['primary'], 
        ha='center', 
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
        (0.05, 0.8),                 # location of annotation box
        xycoords='axes fraction',   # use axes fraction coordinates: relative to axes and percentage of axes for position
        box_alignment=(0.5, 1),       # alignment of the annotation box: (1, 0) means right-aligned and bottom-aligned
        frameon=False               # don't show the frame of the annotation box
    )
    ax.add_artist(ab_belgium_logo)
    
    # North Macedonia logo
    logo_path = project_root / 'static' / 'mkd-logo.png'
    logo = mpimg.imread(logo_path)
    imagebox = OffsetImage(logo, zoom=0.45)
    ab_north_macedonia_logo = AnnotationBbox(
        imagebox, 
        (0.95, 0.8),                 # location of annotation box
        xycoords='axes fraction',   # use axes fraction coordinates: relative to axes and percentage of axes for position
        box_alignment=(0.5, 1),       # alignment of the annotation box: (1, 0) means right-aligned and bottom-aligned
        frameon=False               # don't show the frame of the annotation box
    )
    ax.add_artist(ab_north_macedonia_logo)

def plot_blocks_by_zone(ax, block_analysis, zone_name):
    """
    Plot the blocks by zone.
    """
    # Turn off axis
    # ax.axis('off')

    # Get team colors from styling
    mkd_color = styling.colors["mkd_color"]
    bel_color = styling.colors["bel_color"]

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
        pad_bottom=0.5,
    )
    pitch.draw(ax=ax)

    # Manually reposition the axes to move pitch up and create space below
    pos = ax.get_position()  # Get current position [left, bottom, width, height]
    # Move the axes up by reducing bottom and decreasing height
    ax.set_position([pos.x0, pos.y0 + 0.025, pos.width, pos.height])

    # Plot average player positions
    avg_pos = block_analysis['avg_positions']
    pitch.scatter(
        avg_pos['x'], avg_pos['y'], 
        s=100, 
        color=mkd_color,
        alpha=1, 
        ax=ax, 
        zorder=1
    )

    # Plot defensive line (block_analysis["avg_compactness"]["defensive_line"])
    defensive_line = block_analysis["avg_compactness"]["defensive_line"]
    ax.plot(
        [-34, 34],  # x-coordinates: left to right
        [defensive_line, defensive_line],   # y-coordinates: horizontal line at y=30
        color=mkd_color,
        linewidth=1,
        zorder=1
    )

    # Add metrics below plot
    distance_to_goal = 52.5 - defensive_line
    vertical_spread = block_analysis["avg_compactness"]["vertical_spread"]
    horizontal_spread = block_analysis["avg_compactness"]["horizontal_spread"]
    metrics = [
        ["Defensive line", distance_to_goal],
        ["Vertical spread", vertical_spread],
        ["Horizontal spread", horizontal_spread],
    ]

    for i, metric in enumerate(metrics):
        ax.text(
            0.1, -0.1 - i * 0.13,
            f"{metric[0]}:",
            fontsize=styling.typo["sizes"]["label"],
            fontproperties=styling.fonts['light'],
            ha='left',
            va='top',
            transform=ax.transAxes,  # Use axes coordinates (0-1)
            zorder=1
        )
        ax.text(
            0.9, -0.1 - i * 0.13,
            f"{metric[1]:.1f}m",
            fontsize=styling.typo["sizes"]["label"],
            fontproperties=styling.fonts['medium_italic'],
            ha='right',
            va='top',
            transform=ax.transAxes,  # Use axes coordinates (0-1)
            zorder=1
        )

    # Plot ball positionzone
    zone_boundaries = PitchZones.get_zone_boundaries(zone_name)

    # For VerticalPitch, x and y are swapped:
    # zone x (length) -> plot y (vertical)
    # zone y (width) -> plot x (horizontal)
    length_min, length_max = zone_boundaries['x']  # [17.5, 52.5]
    width_min, width_max = zone_boundaries['y']    # [12, 34]

    # Create Rectangle using the swapped coordinates
    zone_rect = Rectangle(
        (width_min, length_min),      # (x, y) in plot coordinates
        width_max - width_min,         # width in plot
        length_max - length_min,       # height in plot
        facecolor=bel_color,
        alpha=0.1,
        zorder=0,
        transform=ax.transData
    )
    ax.add_patch(zone_rect)