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
        metrics['Metric'].append('Possession %')
        metrics[team1_name].append(round(team1_possession_percentage, 2))
        metrics[team2_name].append(round(team2_possession_percentage, 2))

        # Shot metrics
        shot_metrics = calculate_shot_metrics(events_df, team1_name, team2_name)
        metrics['Metric'].append('xG')
        metrics[team1_name].append(round(shot_metrics['team1_xg'], 2))
        metrics[team2_name].append(round(shot_metrics['team2_xg'], 2))
        metrics['Metric'].append('Total Shots')
        metrics[team1_name].append(shot_metrics['team1_total_shots'])
        metrics[team2_name].append(shot_metrics['team2_total_shots'])
        metrics['Metric'].append('On target Shots')
        metrics[team1_name].append(shot_metrics['team1_on_target_shots'])
        metrics[team2_name].append(shot_metrics['team2_on_target_shots'])
        metrics['Metric'].append('Blocked Shots')
        metrics[team1_name].append(shot_metrics['team1_blocked_shots'])
        metrics[team2_name].append(shot_metrics['team2_blocked_shots'])

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
        The possession percentages for the teams.
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
        logger.debug(f"Possession percentage for {team1_name}: {team1_possession_percentage:.2f}%")
        logger.debug(f"Possession percentage for {team2_name}: {team2_possession_percentage:.2f}%")

        return team1_possession_percentage, team2_possession_percentage

    except Exception as e:
        logger.error(f"Error calculating possession: {e}")
        raise e

def calculate_shot_metrics(events_df: pd.DataFrame, team1_name: str, team2_name: str) -> float:
    """
    Calculate shot metrics for a team.

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
    shot_metrics: dict
        A dictionary with the shot metrics for the teams.
        The keys are:
        - 'xg': float
        - 'total_shots': int
        - 'shots_on_target': int
        - 'blocked_shots': int
        # - 'goals': int
        # - 'shots_inside_box': int
        # - 'shots_outside_box': int
        # - 'shot_accuracy': float
        # - 'conversion_rate': float
    """
    try:
        # Filter for shot events
        shot_events = events_df[events_df['baseTypeName'] == 'SHOT'].copy()

        # Seperate xG from metrics column for each shot
        shot_events['xG'] = shot_events['metrics'].apply(lambda x: x['xG'] if x is not None else 0)
        
        # Filter for team shots
        team1_shot_events = shot_events[shot_events['teamName'] == team1_name]
        team2_shot_events = shot_events[shot_events['teamName'] == team2_name]

        # Calculate total xG for each team
        team1_xg = team1_shot_events['xG'].sum()
        team2_xg = team2_shot_events['xG'].sum()
        
        logger.debug(f"xG for {team1_name}: {team1_xg:.2f}")
        logger.debug(f"xG for {team2_name}: {team2_xg:.2f}")
        
        # Count team shots
        team1_total_shots = len(team1_shot_events)
        team2_total_shots = len(team2_shot_events)

        # Count on target shots
        team1_on_target_shots = len(team1_shot_events[team1_shot_events['shotTypeName'] == 'ON_TARGET'])
        team2_on_target_shots = len(team2_shot_events[team2_shot_events['shotTypeName'] == 'ON_TARGET'])

        # Count blocked shots
        team1_blocked_shots = len(team1_shot_events[team1_shot_events['shotTypeName'] == 'BLOCKED'])
        team2_blocked_shots = len(team2_shot_events[team2_shot_events['shotTypeName'] == 'BLOCKED'])

        logger.debug(f"Total shots: {team1_name}: {team1_total_shots}, {team2_name}: {team2_total_shots}")
        logger.debug(f"On target shots: {team1_name}: {team1_on_target_shots}, {team2_name}: {team2_on_target_shots}")
        logger.debug(f"Blocked shots: {team1_name}: {team1_blocked_shots}, {team2_name}: {team2_blocked_shots}")

        return {
            "team1_xg": team1_xg,
            "team2_xg": team2_xg,
            "team1_total_shots": team1_total_shots,
            "team2_total_shots": team2_total_shots,
            "team1_on_target_shots": team1_on_target_shots,
            "team2_on_target_shots": team2_on_target_shots,
            "team1_blocked_shots": team1_blocked_shots,
            "team2_blocked_shots": team2_blocked_shots,
        }

    except Exception as e:
        logger.error(f"Error calculating xG: {e}")
        raise e