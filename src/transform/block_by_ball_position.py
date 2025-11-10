import logging
import pandas as pd
import numpy as np
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

logger = logging.getLogger(__name__)

# Init zones
ZONES = {
    # Middle third: progression zone
    'left_progression': {'x': [-17.5, 17.5], 'y': [12, 36]},
    'center_progression': {'x': [-17.5, 17.5], 'y': [12, -12]},
    'right_progression': {'x': [-17.5, 17.5], 'y': [-36, -12]},
    
    # Final third
    'left_final_third': {'x': [17.5, 52.5], 'y': [12, 36]},
    'center_final_third': {'x': [17.5, 52.5], 'y': [12, -12]},
    'right_final_third': {'x': [17.5, 52.5], 'y': [-36, -12]},
}

def get_ball_zone(ball_x: float, ball_y: float, zones=ZONES) -> str:
    """
    Get the zone of the ball.
    """
    for zone, coords in zones.items():
        x_min, x_max = coords['x']
        y_min, y_max = coords['y']
        
        if ball_x >= x_min and ball_x <= x_max and ball_y >= y_min and ball_y <= y_max:
            return zone
            
    logger.error(f"Ball ({ball_x}, {ball_y}) not in relevant zones")
    return None

def calculate_convex_hull_area(points):
    """
    Calculate the area of the convex hull.
    """
    if len(points) < 3:
        return None
    try:
        hull = ConvexHull(points)
        return hull.volume  # in 2D is dit de oppervlakte
    except:
        return None

def calculate_team_compactness(team_df):
    """
    Calculate compactness metrics for a team at a moment.
    
    Returns 
    --------
    dict
        A dictionary with the compactness metrics for the team.
        The keys are:
        - area: float (area of the convex hull)
        - vertical_spread: float (difference between highest and lowest player)
        - horizontal_spread: float (difference between leftmost and rightmost player)
        - mean_x: float (mean x coordinate of the players)
        - mean_y: float (mean y coordinate of the players)
        - defensive_line: float (x coordinate of the highest player)
    """
    if len(team_df) < 3:
        return None
    
    points = team_df[['x', 'y']].values
    
    return {
        'area': calculate_convex_hull_area(points),
        'vertical_spread': team_df['x'].max() - team_df['x'].min(),
        'horizontal_spread': team_df['y'].max() - team_df['y'].min(),
        'mean_x': team_df['x'].mean(),
        'mean_y': team_df['y'].mean(),
        'defensive_line': team_df['x'].max(),  # hoogste (meest aanvallende) verdediger
    }

def analyze_block_by_ball_position(
    tracking_df: pd.DataFrame,
    events_df: pd.DataFrame, 
    team1_name: str, 
    team2_name: str
) -> pd.DataFrame:
    """
    Calculate average positions for players for each zone.

    Parameters:
    -----------
    tracking_df: pd.DataFrame
        The tracking dataframe of the game.
    events_df: pd.DataFrame
        The events dataframe of the game.
    team1_name: str
        The name of the first team.
    team2_name: str
        The name of the second team.
    """
    try:
        


        return tracking_df

    except Exception as e:
        logger.error(f"Error analyzing block by ball position: {e}")
        raise e