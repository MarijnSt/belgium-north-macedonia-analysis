import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np
import pandas as pd
from mplsoccer import Pitch
from mplsoccer import VerticalPitch
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
    game_score_ax = fig.add_subplot(gs[1, 1])
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

    game_score_ax.text(
        0.5, 0.5, 
        "Game Score", 
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
    from matplotlib.patches import Rectangle, Ellipse
    
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

    # left_pill = mpatches.FancyBboxPatch((0.35, 0.1), 0.1, 0.5, 
    #                         ec="none",
    #                         boxstyle="Round, pad=0, rounding_size=0.05",
    #                         facecolor=color1,
    #                         # transform=ax.transData,
    #                         # clip_on=False
    #                     )
    # ax.add_patch(left_pill)
    
    # # Pill dimensions
    # pill_width = 0.1  # Width of each pill
    # pill_height = 0.3  # Height - make it small for horizontal pill look
    # gap = 0.05  # Gap between pills
    
    # # Calculate positions - center both pills together
    # total_width = 2 * pill_width + gap
    # left_x = 0.5 - total_width / 2
    # right_x = 0.5 + gap / 2
    # y = 0.5 - pill_height / 2
    
    # # Create pill shapes with high rounding to get capsule effect
    # # The key is rounding_size should be close to height/2 to get semicircular ends
    # left_pill = FancyBboxPatch(
    #     (left_x, y), pill_width, pill_height,
    #     boxstyle=f"round,pad=0,rounding_size={pill_height/2}",
    #     facecolor=color1,
    #     edgecolor='none',
    #     transform=ax.transData,
    #     clip_on=False
    # )
    # ax.add_patch(left_pill)
    
    # right_pill = FancyBboxPatch(
    #     (right_x, y), pill_width, pill_height,
    #     boxstyle=f"round,pad=0,rounding_size={pill_height/2}",
    #     facecolor=color2,
    #     edgecolor='none',
    #     transform=ax.transData,
    #     clip_on=False
    # )
    # ax.add_patch(right_pill)
    
    # # Add team names centered in each pill
    # ax.text(
    #     left_x + pill_width / 2, 0.5,
    #     team1_name,
    #     fontsize=styling.typo["sizes"]["h3"],
    #     color='white',
    #     ha='center',
    #     va='center',
    #     weight='bold',
    #     transform=ax.transData
    # )
    
    # ax.text(
    #     right_x + pill_width / 2, 0.5,
    #     team2_name,
    #     fontsize=styling.typo["sizes"]["h3"],
    #     color='white',
    #     ha='center',
    #     va='center',
    #     weight='bold',
    #     transform=ax.transData
    # )