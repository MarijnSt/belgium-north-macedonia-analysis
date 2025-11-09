import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import numpy as np
import pandas as pd
from mplsoccer import Pitch
from mplsoccer import VerticalPitch
from pathlib import Path
import logging

from config import styling

# Get logger (initialized in source file)
logger = logging.getLogger(__name__)

def create_game_summary(events_df, team1_name, team1_color, team2_name, team2_color, metrics_df):
    """
    Create a comprehensive 3-column game summary.

    Parameters:
    -----------
    events_df: pd.DataFrame
        The events dataframe of the game.
    team1_name: str
        The name of the first team.
    team1_color: str
        The color name in the styling config of the first team.
    team2_name: str
        The name of the second team.
    team2_color: str
        The color name in the styling config of the second team.
    metrics_df: pd.DataFrame
        The metrics dataframe of the game.

    Returns:
    --------
    fig: matplotlib.figure.Figure
        The figure object of the game summary.
    """
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

    # Create figure with GridSpec - 3 columns, 3 rows
    fig = plt.figure(figsize=(24, 18))
    gs = fig.add_gridspec(7, 3, hspace=0.35, wspace=0.3, 
                  height_ratios=[0.5, 1, 1, 1, 1, 1, 1], width_ratios=[1, 1.2, 1])

    # Init axis
    heading_ax = fig.add_subplot(gs[0, :])
    team1_passing_network_ax = fig.add_subplot(gs[1:4, 0])
    team1_shot_map_ax = fig.add_subplot(gs[4:7, 0])
    team2_passing_network_ax = fig.add_subplot(gs[1:4, 2])
    team2_shot_map_ax = fig.add_subplot(gs[4:7, 2])
    game_info_ax = fig.add_subplot(gs[1, 1])
    territorial_heatmap_ax = fig.add_subplot(gs[2:4, 1])
    stats_comparison_ax = fig.add_subplot(gs[4:7, 1])

    # Add text to each axis    
    team1_passing_network_ax.text(
        0.5, 0.5, 
        f"{team1_name} - Passing Network", 
        fontsize=styling.typo["sizes"]["p"], 
        color=styling.colors["primary"], 
        ha="center", 
        va="center"
    )

    team1_shot_map_ax.text(
        0.5, 0.5, 
        f"{team1_name} - Shot Map", 
        fontsize=styling.typo["sizes"]["p"], 
        color=styling.colors["primary"], 
        ha="center", 
        va="center"
    )

    team2_passing_network_ax.text(
        0.5, 0.5, 
        f"{team2_name} - Passing Network", 
        fontsize=styling.typo["sizes"]["p"], 
        color=styling.colors["primary"], 
        ha="center", 
        va="center"
    )

    team2_shot_map_ax.text(
        0.5, 0.5, 
        f"{team2_name} - Shot Map", 
        fontsize=styling.typo["sizes"]["p"], 
        color=styling.colors["primary"], 
        ha="center", 
        va="center"
    )

    territorial_heatmap_ax.text(
        0.5, 0.5, 
        "Territorial Heatmap", 
        fontsize=styling.typo["sizes"]["p"], 
        color=styling.colors["primary"], 
        ha="center", 
        va="center"
    )

    stats_comparison_ax.text(
        0.5, 0.5, 
        "Stats Comparison", 
        fontsize=styling.typo["sizes"]["p"], 
        color=styling.colors["primary"], 
        ha="center", 
        va="center"
    )

    # Plot heading
    plot_heading(heading_ax, team1_name, team2_name, team1_color, team2_color)

    # Plot game info
    plot_game_info(game_info_ax, metrics_df)

    return fig


def plot_heading(ax, team1_name, team2_name, team1_color, team2_color):
    """
    Plot the heading with pill-shaped team name badges.

    Parameters:
    -----------
    ax: matplotlib.axes.Axes
        The axis to plot on.
    team1_name: str
        The name of the first team.
    team2_name: str
        The name of the second team.
    team1_color: str
        The color name in the styling config of the first team.
    team2_color: str
        The color name in the styling config of the second team.
    """    
    # Turn off axis
    ax.axis('off')
    
    # Get team colors from styling
    color1 = styling.colors[team1_color]
    color2 = styling.colors[team2_color]

    # Left pill
    ax.add_patch(Rectangle((0.325, 0), 0.15, 0.65, facecolor=color1, edgecolor='none'))
    ax.add_patch(Ellipse((0.325, 0.325), width=0.022, height=0.65, facecolor=color1, edgecolor='none'))
    ax.add_patch(Ellipse((0.475, 0.325), width=0.022, height=0.65, facecolor=color1, edgecolor='none'))
    ax.text(0.4, 0.325, 
        team1_name, 
        fontsize=styling.typo["sizes"]["h1"],
        fontproperties=styling.fonts['medium_italic'],
        color='white', 
        ha='center', 
        va='center',
    )
    
    # Right pill
    ax.add_patch(Rectangle((0.525, 0), 0.15, 0.65, facecolor=color2, edgecolor='none'))
    ax.add_patch(Ellipse((0.525, 0.325), width=0.022, height=0.65, facecolor=color2, edgecolor='none'))
    ax.add_patch(Ellipse((0.675, 0.325), width=0.022, height=0.65, facecolor=color2, edgecolor='none'))
    ax.text(0.6, 0.325, 
        team2_name, 
        fontsize=styling.typo["sizes"]["h1"],
        fontproperties=styling.fonts['medium_italic'],
        color='white',
        ha='center',
        va='center',
    )

def plot_game_info(ax, metrics_df):
    """
    Plot the game info.
    """
    # Turn off axis
    ax.axis('off')

    # Belgium logo
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    logo_path = project_root / 'static' / 'bel-logo.png'
    logo = mpimg.imread(logo_path)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab_belgium_logo = AnnotationBbox(
        imagebox, 
        (0.175, 1),                 # location of annotation box
        xycoords='axes fraction',   # use axes fraction coordinates: relative to axes and percentage of axes for position
        box_alignment=(0.5, 1),       # alignment of the annotation box: (1, 0) means right-aligned and bottom-aligned
        frameon=False               # don't show the frame of the annotation box
    )
    ax.add_artist(ab_belgium_logo)
    
    # North Macedonia logo
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    logo_path = project_root / 'static' / 'mkd-logo.png'
    logo = mpimg.imread(logo_path)
    imagebox = OffsetImage(logo, zoom=0.45)
    ab_north_macedonia_logo = AnnotationBbox(
        imagebox, 
        (0.825, 1),                 # location of annotation box
        xycoords='axes fraction',   # use axes fraction coordinates: relative to axes and percentage of axes for position
        box_alignment=(0.5, 1),       # alignment of the annotation box: (1, 0) means right-aligned and bottom-aligned
        frameon=False               # don't show the frame of the annotation box
    )
    ax.add_artist(ab_north_macedonia_logo)

    # Score
    ax.text(0.5, 0.9, 
        "0 - 0", 
        fontsize=styling.typo["sizes"]["h0"],
        fontproperties=styling.fonts['bold'],
        color=styling.colors["primary"],
        ha="center",
        va="top"
    )

    # Competition
    ax.text(0.5, 0.45, 
        "World Cup Qualifiers", 
        fontsize=styling.typo["sizes"]["p"],
        fontproperties=styling.fonts['medium'],
        color=styling.colors["primary"],
        ha="center",
        va="top",
    )

    # Date
    ax.text(0.5, 0.25, 
        "10/10/2025", 
        fontsize=styling.typo["sizes"]["p"],
        fontproperties=styling.fonts['medium'],
        color=styling.colors["primary"],
        ha="center",
        va="top",
    )