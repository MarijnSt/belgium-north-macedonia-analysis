import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
import logging

# Get logger (initialized in source file)
logger = logging.getLogger(__name__)

def calculate_dominance_metrics(events_df: pd.DataFrame, team1_name: str, team2_name: str) -> pd.DataFrame:
    """
    Calculate all dominance metrics for both teams and return as comparison DataFrame.

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
    pd.DataFrame
        A dataframe with the dominance metrics for both teams.
    """
    try:
        metrics = {
            'Metric': [],
            team1_name: [],
            team2_name: []
        }

        # Possession
        team1_possession_percentage, team2_possession_percentage = calculate_possession(events_df, team1_name, team2_name)
        metrics['Metric'].append('Possession')
        metrics[team1_name].append(round(team1_possession_percentage, 2))
        metrics[team2_name].append(round(team2_possession_percentage, 2))

        return pd.DataFrame(metrics)
    
    except Exception as e:
        logger.error(f"Error calculating dominance metrics: {e}")
        raise e

def calculate_possession(events_df: pd.DataFrame, team1_name: str, team2_name: str) -> float:
    """
    Calculate possession percentage for a team.
    This will be calculated based on the start and end timings for each event.

    Parameters:
    -----------
    events_df: pd.DataFrame
        The events dataframe of the game.
    team1_name: str
        The name of the team.
    team2_name: str
        The name of the second team.

    Returns:
    --------
    float
        The possession percentage for the team.
    """
    try:
        # Only look at possession events
        possession_events = ['PASS', 'DRIBBLE', 'TAKE_ON', 'CARRY', 'TOUCH']
        poss_df = events_df[events_df['baseTypeName'].isin(possession_events)].copy()

        # Calculate possession duration for each event
        poss_df['duration_ms'] = poss_df['endTimeMs'] - poss_df['startTimeMs']

        # Calculate the total and team possession duration
        team1_possession_duration = poss_df[poss_df['teamName'] == team1_name]['duration_ms'].sum()
        team2_possession_duration = poss_df[poss_df['teamName'] == team2_name]['duration_ms'].sum()
        total_possession_duration = poss_df['duration_ms'].sum()
        
        # Calculate possession percentage
        team1_possession_percentage = (team1_possession_duration / total_possession_duration) * 100
        team2_possession_percentage = (team2_possession_duration / total_possession_duration) * 100
        logger.info(f"Possession percentage for {team1_name}: {team1_possession_percentage:.2f}%")
        logger.info(f"Possession percentage for {team2_name}: {team2_possession_percentage:.2f}%")

        return team1_possession_percentage, team2_possession_percentage

    except Exception as e:
        logger.error(f"Error calculating possession: {e}")
        raise e