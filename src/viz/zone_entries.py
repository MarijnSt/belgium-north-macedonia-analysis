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

def plot_zone_entries(zone_entries_df: pd.DataFrame, zone_entry_stats: pd.DataFrame, team_name: str):
    """
    Plot the zone entries and the stats per zone.

    Parameters:
    -----------
    zone_entries_df: pd.DataFrame
        The dataframe with the zone entries data.
    zone_entry_stats: pd.DataFrame
        The dataframe with the zone entry stats.
    team_name: str
        The name of the team.
    
    Returns:
    --------
    fig: matplotlib.figure.Figure
        The figure object of the zone entries and the stats per zone.
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
        fig = plt.figure(figsize=(11, 14))
        gs = fig.add_gridspec(3, 1, hspace=0.35, wspace=0.3, 
                    height_ratios=[0.25, 1, 1])

        # Init axis
        heading_ax = fig.add_subplot(gs[0, :])
        zone_entries_ax = fig.add_subplot(gs[1, :])
        zone_entry_stats_ax = fig.add_subplot(gs[2, :])

        # Plot heading
        plot_heading(heading_ax, team_name)

        # # Plot zone entries
        # plot_zone_entries(zone_entries_ax, zone_entries_df)

        # # Plot zone entry stats
        # plot_zone_entry_stats(zone_entry_stats_ax, zone_entry_stats)

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
        0, 0.5,
        f"How did we attack the low block?", 
        fontsize=styling.typo["sizes"]["h1"], 
        fontproperties=styling.fonts['medium_italic'], 
        color=styling.colors['primary'], 
        ha='left', 
        va='center',
    )

    # Plot subtitle
    ax.text(
        0, 0.05,
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


