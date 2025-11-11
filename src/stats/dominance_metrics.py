import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
import logging

from transform import get_final_third_entries

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
        # Init team dictionaries
        team1_metrics = {"team": team1_name}
        team2_metrics = {"team": team2_name}

        # Possession
        team1_possession_percentage, team2_possession_percentage = calculate_possession(events_df, team1_name, team2_name)
        team1_metrics['possession'] = round(team1_possession_percentage, 2)
        team2_metrics['possession'] = round(team2_possession_percentage, 2)

        # Field tilt
        field_tilt = calculate_field_tilt(events_df, team1_name, team2_name)
        team1_metrics['field_tilt'] = round(field_tilt['team1_field_tilt'], 2)
        team2_metrics['field_tilt'] = round(field_tilt['team2_field_tilt'], 2)

        # Successful passes
        successful_passes = calculate_successful_passes(events_df, team1_name, team2_name)
        team1_metrics['successful_passes'] = successful_passes['team1_successful_passes']
        team2_metrics['successful_passes'] = successful_passes['team2_successful_passes']

        # Final third entries
        final_third_entries = calculate_final_third_entries(events_df, team1_name, team2_name)
        team1_metrics['final_third_entries'] = final_third_entries['team1_final_third_entries']
        team2_metrics['final_third_entries'] = final_third_entries['team2_final_third_entries']

        # Box touches
        box_touches = calculate_box_touches(events_df, team1_name, team2_name)
        team1_metrics['box_touches'] = box_touches['team1_box_touches']
        team2_metrics['box_touches'] = box_touches['team2_box_touches']

        # Progressive passes
        prog_passes = calculate_progressive_passes(events_df, team1_name, team2_name)
        team1_metrics['progressive_passes'] = prog_passes['team1_prog_passes']
        team2_metrics['progressive_passes'] = prog_passes['team2_prog_passes']

        team1_metrics["pp_ratio"] = prog_passes['team1_prog_passes'] / successful_passes['team1_successful_passes']
        team2_metrics["pp_ratio"] = prog_passes['team2_prog_passes'] / successful_passes['team2_successful_passes']

        team1_metrics['pp_outside_final_third'] = prog_passes['team1_prog_passes_outside_final_third']
        team2_metrics['pp_outside_final_third'] = prog_passes['team2_prog_passes_outside_final_third']

        team1_metrics['pp_in_final_third'] = prog_passes['team1_prog_passes_in_final_third']
        team2_metrics['pp_in_final_third'] = prog_passes['team2_prog_passes_in_final_third']

        # Shot metrics
        shot_metrics = calculate_shot_metrics(events_df, team1_name, team2_name)
        team1_metrics['xG'] = round(shot_metrics['team1_xg'], 2)
        team2_metrics['xG'] = round(shot_metrics['team2_xg'], 2)

        team1_metrics['total_shots'] = shot_metrics['team1_total_shots']
        team2_metrics['total_shots'] = shot_metrics['team2_total_shots']

        team1_metrics['on_target_shots'] = shot_metrics['team1_on_target_shots']
        team2_metrics['on_target_shots'] = shot_metrics['team2_on_target_shots']

        team1_metrics['blocked_shots'] = shot_metrics['team1_blocked_shots']
        team2_metrics['blocked_shots'] = shot_metrics['team2_blocked_shots']

        # PPDA
        ppda = calculate_ppda(events_df, team1_name, team2_name)
        team1_metrics['ppda'] = round(ppda['team1_ppda'], 2)
        team2_metrics['ppda'] = round(ppda['team2_ppda'], 2)

        return pd.DataFrame([team1_metrics, team2_metrics])
    
    except Exception as e:
        logger.error(f"Error calculating dominance metrics: {e}")
        raise e

def calculate_successful_passes(events_df: pd.DataFrame, team1_name: str, team2_name: str) -> float:
    """
    Calculate successful passes for a team.

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
    int
        The number of successful passes for the teams.
    """
    try:
        # Get passes
        passes = events_df[
            (events_df["baseTypeName"] == "PASS") &
            (events_df["resultName"] == "SUCCESSFUL")
        ]

        # Count passes
        team1_passes = len(passes[passes["teamName"] == team1_name])
        team2_passes = len(passes[passes["teamName"] == team2_name])

        logger.debug(f"Successful passes for {team1_name}: {team1_passes}")
        logger.debug(f"Successful passes for {team2_name}: {team2_passes}")

        return {
            "team1_successful_passes": team1_passes,
            "team2_successful_passes": team2_passes,
        }

    except Exception as e:
        logger.error(f"Error calculating passes: {e}")

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

def calculate_field_tilt(events_df: pd.DataFrame, team1_name: str, team2_name: str) -> float:
    """
    Calculate field tilt for a team.

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
    float
        The field tilt for the teams.
    """
    try:
        # Get passes in final third
        passes_in_final_third = events_df[
            (events_df["baseTypeName"] == "PASS") &
            (events_df["endPosXM"] >= 17.5)
        ]

        logger.debug(f"Passes in final third: {len(passes_in_final_third)}")

        # Count passes
        total_passes = len(passes_in_final_third)
        team1_passes = len(passes_in_final_third[passes_in_final_third["teamName"] == team1_name])
        team2_passes = len(passes_in_final_third[passes_in_final_third["teamName"] == team2_name])

        # Calculate field tilt
        team1_field_tilt = (team1_passes / total_passes) * 100
        team2_field_tilt = (team2_passes / total_passes) * 100

        logger.debug(f"Field tilt for {team1_name}: {team1_field_tilt:.2f}%")
        logger.debug(f"Field tilt for {team2_name}: {team2_field_tilt:.2f}%")

        return {
            "team1_field_tilt": team1_field_tilt,
            "team2_field_tilt": team2_field_tilt,
        }

    except Exception as e:
        logger.error(f"Error calculating field tilt: {e}")
        raise e

def calculate_final_third_entries(events_df: pd.DataFrame, team1_name: str, team2_name: str) -> float:
    """
    Calculate final third entries for a team.

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
    float
        The final third entries for the teams.
    """
    try:
        # Get final third entries
        final_third_entries_df = get_final_third_entries(events_df)

        logger.debug(f"Final third entries: {len(final_third_entries_df)}")

        # Count final third entries
        team1_final_third_entries = len(final_third_entries_df[final_third_entries_df["teamName"] == team1_name])
        team2_final_third_entries = len(final_third_entries_df[final_third_entries_df["teamName"] == team2_name])

        logger.debug(f"Final third entries for {team1_name}: {team1_final_third_entries}")
        logger.debug(f"Final third entries for {team2_name}: {team2_final_third_entries}")

        return {
            "team1_final_third_entries": team1_final_third_entries,
            "team2_final_third_entries": team2_final_third_entries,
        }
    
    except Exception as e:
        logger.error(f"Error calculating final third entries: {e}")
        raise e

def calculate_box_touches(events_df: pd.DataFrame, team1_name: str, team2_name: str) -> float:
    """
    Calculate box touches for a team.

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
    float
        The box touches for the teams.
    """
    try:
        # Filter for box touches
        touch_events = ['PASS', 'DRIBBLE', 'TAKE_ON', 'CARRY', 'TOUCH']
        box_touches_df = events_df[
            events_df['baseTypeName'].isin(touch_events) &
            (events_df['startPosXM'] >= 36) &
            (events_df['startPosYM'] >= -20.16) &
            (events_df['startPosYM'] <= 20.16)
        ]

        logger.debug(f"Box touches: {len(box_touches_df)}")

        # Count box touches
        team1_box_touches = len(box_touches_df[box_touches_df["teamName"] == team1_name])
        team2_box_touches = len(box_touches_df[box_touches_df["teamName"] == team2_name])

        logger.debug(f"Box touches for {team1_name}: {team1_box_touches}")
        logger.debug(f"Box touches for {team2_name}: {team2_box_touches}")

        return {
            "team1_box_touches": team1_box_touches,
            "team2_box_touches": team2_box_touches,
        }
    
    except Exception as e:
        logger.error(f"Error calculating box touches: {e}")
        raise e

def calculate_progressive_passes(events_df: pd.DataFrame, team1_name: str, team2_name: str) -> float:
    """
    Calculate progressive passes for a team.

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
    float
        The progressive passes for the teams.
    """
    try:
        # Filter out passes
        passes = events_df[
            (events_df["baseTypeName"] == "PASS") &
            (events_df["resultName"] == "SUCCESSFUL")
        ].copy()
        passes["progress"] = passes["endPosXM"] - passes["startPosXM"]

        # Filter for progressive passes outside the final third
        prog_passes_outside_final_third = passes[
            (passes["endPosXM"] < 17.5) &
            (passes["progress"] >= 10)
        ]

        # Filter for progressive passes inside the final third
        prog_passes_in_final_third = passes[
            (passes["endPosXM"] < 17.5) &
            (passes["progress"] >= 5)
        ]

        # Count progressive passes
        team1_prog_passes_outside_final_third = len(prog_passes_outside_final_third[prog_passes_outside_final_third["teamName"] == team1_name])
        team2_prog_passes_outside_final_third = len(prog_passes_outside_final_third[prog_passes_outside_final_third["teamName"] == team2_name])
        team1_prog_passes_in_final_third = len(prog_passes_in_final_third[prog_passes_in_final_third["teamName"] == team1_name])
        team2_prog_passes_in_final_third = len(prog_passes_in_final_third[prog_passes_in_final_third["teamName"] == team2_name])

        team1_prog_passes = team1_prog_passes_outside_final_third + team1_prog_passes_in_final_third
        team2_prog_passes = team2_prog_passes_outside_final_third + team2_prog_passes_in_final_third

        logger.debug(f"Progressive passes for {team1_name}: {team1_prog_passes}")
        logger.debug(f"Progressive passes for {team2_name}: {team2_prog_passes}")

        return {
            "team1_prog_passes": team1_prog_passes,
            "team2_prog_passes": team2_prog_passes,
            "team1_prog_passes_outside_final_third": team1_prog_passes_outside_final_third,
            "team2_prog_passes_outside_final_third": team2_prog_passes_outside_final_third,
            "team1_prog_passes_in_final_third": team1_prog_passes_in_final_third,
            "team2_prog_passes_in_final_third": team2_prog_passes_in_final_third,
        }
    
    except Exception as e:
        logger.error(f"Error calculating progressive passes: {e}")
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

def calculate_ppda(events_df: pd.DataFrame, team1_name: str, team2_name: str) -> float:
    """
    Calculate PPDA (Passes Allowed Per Defensive Action) for a team. Cutoff is 60% of the field.

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
    float
        The PPDA for the teams.
    """
    try:
        # Filter for succesful passes in buildup and progression thirds
        passes_df = events_df[
            (events_df["baseTypeName"] == "PASS") &
            (events_df["resultName"] == "SUCCESSFUL") &
            (events_df["startPosXM"] < 10.5)
        ]

        clearances_df = events_df[
            (events_df["baseTypeName"] == "CLEARANCE") &
            (events_df["startPosXM"] < 10.5)
        ]

        passes_team1 = len(passes_df[passes_df["teamName"] == team1_name])
        passes_team2 = len(passes_df[passes_df["teamName"] == team2_name])
        passes_team1 += len(clearances_df[clearances_df["teamName"] == team1_name])
        passes_team2 += len(clearances_df[clearances_df["teamName"] == team2_name])

        logger.debug(f"Passes: {team1_name} - {passes_team1}, {team2_name} - {passes_team2}")

        # Filter for defensive actions in opposition buildup and progression thirds
        # Tackle: 400 (geslaagd)
        # Challenge: 401 (niet geslaagd)
        # Interception: 500 (verschil met recovery?)
        # Recovery: 501 (geslaagd)
        # Foul: 700
        # Blocked pass: 1302
        defensive_actions_df = events_df[
            (events_df["subTypeId"].isin([400, 401, 500, 501, 700, 1302])) &
            (events_df["startPosXM"] >= -10.5)
        ]

        defensive_actions_team1 = len(defensive_actions_df[defensive_actions_df["teamName"] == team1_name])
        defensive_actions_team2 = len(defensive_actions_df[defensive_actions_df["teamName"] == team2_name])
        
        logger.debug(f"Defensive actions: {team1_name} - {defensive_actions_team1}, {team2_name} - {defensive_actions_team2}")

        # Calculate PPDA
        ppda_team1 = passes_team2 / defensive_actions_team1
        ppda_team2 = passes_team1 / defensive_actions_team2

        logger.debug(f"PPDA: {team1_name} - {ppda_team1}, {team2_name} - {ppda_team2}")

        return {
            "team1_ppda": ppda_team1,
            "team2_ppda": ppda_team2,
        }


    except Exception as e:
        logger.error(f"Error calculating PPDA: {e}")
        raise e