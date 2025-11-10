import logging

logger = logging.getLogger(__name__)

def get_territorial_heatmap_data(events_df, team1_name, team2_name):
    """
    Get possession events for the territorial heatmap.

    Parameters:
    -----------
    events_df: pd.DataFrame
        The events dataframe of the game.
    team1_name: str
        The name of the first team.
    team2_name: str
        The name of the second team.

    Returns:
    --------
    df_team1: pd.DataFrame
        The events dataframe for team1.
    df_team2: pd.DataFrame
        The events dataframe for team2.
    """
    try:
        possession_events = ['PASS', 'DRIBBLE', 'TAKE_ON', 'CARRY', 'TOUCH']
    
        # Get possession events for team1
        df_team1 = events_df[(events_df['teamName'] == team1_name) & 
                            (events_df['baseTypeName'].isin(possession_events)) &
                            (events_df['startPosXM'].notna()) & 
                            (events_df['startPosYM'].notna())].copy()
        
        # Get possession events for team2
        df_team2 = events_df[(events_df['teamName'] == team2_name) & 
                            (events_df['baseTypeName'].isin(possession_events)) &
                            (events_df['startPosXM'].notna()) & 
                            (events_df['startPosYM'].notna())].copy()

        # Flip coordinates for team2
        df_team2['startPosXM'] = df_team2['startPosXM'] * -1
        df_team2['startPosYM'] = df_team2['startPosYM'] * -1
        
        return df_team1, df_team2

    except Exception as e:
        logger.error(f"Error getting territorial heatmap data: {e}")
        raise e