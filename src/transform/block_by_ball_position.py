import logging
import pandas as pd

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