import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd
from mplsoccer import Pitch
from mplsoccer import VerticalPitch
from pathlib import Path
import logging
from scipy.ndimage import gaussian_filter

from config import styling
from transform import get_passing_network_data, get_territorial_heatmap_data

# Get logger (initialized in source file)
logger = logging.getLogger(__name__)

def create_game_summary(events_df, player_data, team1_name, team1_color, team2_name, team2_color, metrics_df):
    """
    Create a comprehensive 3-column game summary.

    Parameters:
    -----------
    events_df: pd.DataFrame
        The events dataframe of the game.
    player_data: pd.DataFrame
        The player dataframe of the game.
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
    team1_shot_map_ax.text(
        0.5, 0.5, 
        f"{team1_name} - Shot Map", 
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

    # Plot heading
    plot_heading(heading_ax, team1_name, team2_name, team1_color, team2_color)

    # Plot game info
    plot_game_info(game_info_ax)

    # Plot passing network
    plot_passing_network(team1_passing_network_ax, events_df, player_data, team1_name, team1_color)
    plot_passing_network(team2_passing_network_ax, events_df, player_data, team2_name, team2_color)

    # Plot territorial heatmap
    plot_territorial_heatmap(territorial_heatmap_ax, events_df, team1_name, team2_name, team1_color, team2_color)
    
    # Plot stats comparison
    plot_stats_comparison(stats_comparison_ax, metrics_df, team1_name, team2_name, team1_color, team2_color)

    return fig


def plot_heading(ax, team1_name, team2_name, team1_color, team2_color):
    """
    Plot the heading with pill-shaped team names.
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

def plot_game_info(ax):
    """
    Plot the game info: logos, score, competition and date.
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

def plot_passing_network(ax, events_df, player_data, team_name, team_color):
    """
    Plot the passing network.
    """
    # Turn off axis
    # ax.axis('off')

    # Get team colors from styling
    color = styling.colors[team_color]

    pitch = VerticalPitch(
        pitch_type=styling.pitch['pitch_type'],
        pitch_length=styling.pitch['pitch_length'],
        pitch_width=styling.pitch['pitch_width'],
        line_color=styling.pitch['line_color'], 
        linewidth=styling.pitch['linewidth'], 
        goal_type=styling.pitch['goal_type'], 
        corner_arcs=styling.pitch['corner_arcs'],
    )
    pitch.draw(ax=ax)

    # Create scatter and lines data
    scatter_df, lines_df = get_passing_network_data(events_df, player_data, team_name)

    # Scatter the location on the pitch
    pitch.scatter(scatter_df.x, scatter_df.y, s=scatter_df.marker_size, color=color, edgecolors=None, linewidth=1, alpha=1, ax=ax, zorder=3)
    
    # Annotating player number
    for i, row in scatter_df.iterrows():
        pitch.annotate(
            int(row.playerShirtNumber), 
            xy=(row.x, row.y), 
            c='white', 
            va='center', 
            ha='center',  
            size=styling.typo['sizes']['p'],
            fontproperties=styling.fonts['medium_italic'],
            ax=ax, 
            zorder=4
        )
    
    # Plot lines between players
    for i, row in lines_df.iterrows():
        # Get player shirt numbers
        player1 = int(row["pair_key"].split("_")[0])
        player2 = int(row['pair_key'].split("_")[1])
        # Take the average location of players to plot a line between them
        player1_x = scatter_df.loc[scatter_df["playerShirtNumber"] == player1]['x'].iloc[0]
        player1_y = scatter_df.loc[scatter_df["playerShirtNumber"] == player1]['y'].iloc[0]
        player2_x = scatter_df.loc[scatter_df["playerShirtNumber"] == player2]['x'].iloc[0]
        player2_y = scatter_df.loc[scatter_df["playerShirtNumber"] == player2]['y'].iloc[0]
        num_passes = row["pass_count"]
        
        # Set line width
        line_width = (num_passes / lines_df['pass_count'].max() * 5)
        
        # Plot lines on the pitch
        pitch.lines(player1_x, player1_y, player2_x, player2_y, alpha=1, lw=line_width, zorder=2, color=color, ax=ax)

def plot_territorial_heatmap(ax, events_df, team1_name, team2_name, team1_color, team2_color):
    """
    Plot a territorial heatmap showing pitch control by both teams.
    
    Parameters:
    -----------
    ax: matplotlib.axes.Axes
        The axis to plot on
    events_df: pd.DataFrame
        The events dataframe
    team1_name: str
        Name of the first team
    team2_name: str
        Name of the second team
    team1_color: str
        Color key for team1 in styling
    team2_color: str
        Color key for team2 in styling
    """    
    # Get team colors from styling
    color1 = styling.colors[team1_color]
    color2 = styling.colors[team2_color]
    
    # Create pitch
    pitch = Pitch(
        pitch_type=styling.pitch['pitch_type'],
        pitch_length=styling.pitch['pitch_length'],
        pitch_width=styling.pitch['pitch_width'],
        line_color=styling.pitch['line_color'], 
        linewidth=styling.pitch['linewidth'], 
        goal_type=styling.pitch['goal_type'], 
        corner_arcs=styling.pitch['corner_arcs'],
    )
    pitch.draw(ax=ax)
    
    # Filter events with location data
    df_team1, df_team2 = get_territorial_heatmap_data(events_df, team1_name, team2_name)
    
    # Use finer bins for smoother result
    bins_x = 60
    bins_y = 40
    
    # SecondSpectrum coordinates are centered at 0
    x_range = [-styling.pitch['pitch_length']/2, styling.pitch['pitch_length']/2]
    y_range = [-styling.pitch['pitch_width']/2, styling.pitch['pitch_width']/2]
    
    # Create 2D histogram for each team
    heatmap_team1, xedges, yedges = np.histogram2d(
        df_team1['startPosXM'], 
        df_team1['startPosYM'],
        bins=[bins_x, bins_y],
        range=[x_range, y_range]
    )
    
    heatmap_team2, _, _ = np.histogram2d(
        df_team2['startPosXM'], 
        df_team2['startPosYM'],
        bins=[bins_x, bins_y],
        range=[x_range, y_range]
    )
    
    # Apply strong Gaussian smoothing for that blurred look
    sigma = 3
    heatmap_team1_smooth = gaussian_filter(heatmap_team1, sigma=sigma)
    heatmap_team2_smooth = gaussian_filter(heatmap_team2, sigma=sigma)
    
    # Calculate dominance: positive values = team1, negative = team2
    total = heatmap_team1_smooth + heatmap_team2_smooth
    # Avoid division by zero
    dominance = np.divide(
        heatmap_team1_smooth - heatmap_team2_smooth, 
        total, 
        out=np.zeros_like(total), 
        where=total != 0
    )
    
    # Create a diverging colormap
    colors = [color2, '#FFFFFF', color1]
    n_bins = 256
    cmap = LinearSegmentedColormap.from_list('territorial', colors, N=n_bins)
    
    extent = [x_range[0], x_range[1], y_range[0], y_range[1]]
    
    ax.imshow(
        dominance.T,
        extent=extent,
        origin='lower',
        cmap=cmap,
        vmin=-1,
        vmax=1,
        alpha=0.6,
        aspect='auto',
        zorder=1,
        interpolation='bilinear' 
    )

    ax.text(0, -37.5, 
        f"Territorial Heatmap: {team1_name} attacking from left to right", 
        fontsize=styling.typo["sizes"]["p"], 
        color=styling.colors["primary"], 
        ha="center", 
        va="center"
    )

def plot_stats_comparison(ax, metrics_df, team1_name, team2_name, team1_color, team2_color):
    """
    Plot the stats comparison.
    """
    # Turn off axis
    ax.axis('off')

    # Get team colors from styling
    color1 = styling.colors[team1_color]
    color2 = styling.colors[team2_color]

    # Define which stats to display and their labels
    stats_to_plot = [
        ('possession', 'Ball possession'),
        ('field_tilt', 'Field tilt'),
        ('xG', 'Expected goals'),
        ('total_shots', 'Total shots'),
        ('on_target_shots', 'On target shots'),
        ('ppda', 'Passes allowed per defensive action'),
        ('final_third_entries', 'Final third entries'),
        ('box_touches', 'Box touches'),
        ('progressive_passes', 'Progressive passes')
    ]
    
    # Get team data
    team1_data = metrics_df[metrics_df['team'] == team1_name].iloc[0]
    team2_data = metrics_df[metrics_df['team'] == team2_name].iloc[0]
    
    bar_height = 0.5
    scatter_size = 475
    
    for i, (stat, label) in enumerate(stats_to_plot):
        y_pos = len(stats_to_plot) - 1 - i  # Reverse order to match typical display
        
        # Get values and normalize
        val1 = team1_data[stat]
        val2 = team2_data[stat]
        total = val1 + val2
        
        norm_val1 = val1 / total
        norm_val2 = val2 / total
        
        # Create stat bars for each team
        ax.barh(y_pos, norm_val1, height=bar_height, color=color1, align='center', zorder=2)
        ax.barh(y_pos, norm_val2, height=bar_height, left=norm_val1, color=color2, align='center', zorder=2)
        
        # Add rounded edges using scatter points
        ax.scatter(0, y_pos, s=scatter_size, color=color1, zorder=3, marker='o')
        ax.scatter(1, y_pos, s=scatter_size, color=color2, zorder=1, marker='o')
        
        # Middle junction (where colors meet)
        ax.scatter(norm_val1, y_pos, s=scatter_size, color=color1, zorder=3, marker='o')
        
        # Set labels (decimal points, percentages, etc.)
        label1 = f"{val1:.0f}"
        label2 = f"{val2:.0f}"
        # Percentage labels
        if stat in ['possession', 'field_tilt']:
            label1 = f"{val1:.0f}%"
            label2 = f"{val2:.0f}%"
        # Decimal points
        if stat in ['xG', 'ppda']:
            label1 = f"{val1:.2f}"
            label2 = f"{val2:.2f}"

        # Label for team 1 (left side)
        ax.text(0.02, y_pos, 
            label1, 
            va='center', 
            ha='left', 
            fontsize=styling.typo["sizes"]["h4"], 
            fontproperties=styling.fonts['medium_italic'],
            color='white', 
            zorder=4
        )
        
        # Label for team 2 (right side)
        ax.text(0.98, y_pos, 
            label2,
            va='center', 
            ha='right', 
            fontsize=styling.typo["sizes"]["h4"], 
            fontproperties=styling.fonts['medium_italic'],
            color='white', 
            zorder=4
        )
        
        # Add stat label in the center
        ax.text(0.5, y_pos,
            label,
            va='center', 
            ha='center', 
            fontsize=styling.typo["sizes"]["h4"], 
            fontproperties=styling.fonts['medium_italic'],
            color='#ffffff', 
            zorder=4
        )
    
        # Styling
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.5, len(stats_to_plot) - 0.5)

