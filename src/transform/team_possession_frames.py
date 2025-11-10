import pandas as pd
import logging

logger = logging.getLogger(__name__)

def get_possession_frames(tracking_df: pd.DataFrame, possessing_team_name: str = 'Belgium') -> list[int]:
    """
    Get the possession frames for a team.
    """    
    possession_frames = tracking_df[
        tracking_df['last_touch'] == possessing_team_name
    ]['frame_id'].unique()

    logger.debug(f"Found {len(possession_frames)} unique possession frame ids for {possessing_team_name}")
    
    return possession_frames