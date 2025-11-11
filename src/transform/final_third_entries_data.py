import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

def get_final_third_entries(events_df):
    """
    Get the final third entries.

    Parameters:
    -----------
    events_df: pd.DataFrame
        The events dataframe.

    Returns:
    --------
    pd.DataFrame
        The dataframe with the final third entries.
    """
    try:
        # Filter for final third entries
        final_third_entries = events_df[
            (events_df["baseTypeName"].isin(["PASS", "DRIBBLE"])) &
            (events_df["resultId"] == 1) &
            (events_df["startPosXM"] < 17.5) &
            (events_df["endPosXM"] >= 17.5)
        ].copy()

        logger.debug(f"Found {len(final_third_entries)} final third entries")

        # Get xA from metrics column
        final_third_entries["xA"] = final_third_entries["metrics"].apply(lambda x: x["xA"] if x is not None else 0)

        columns = [
            "eventId",
            "timestamp",
            "teamName",
            "baseTypeName",
            "subTypeName",
            "resultName",
            "startPosXM",
            "endPosXM",
            "startPosYM",
            "endPosYM",
            "sequenceId",
            "sequenceStart",
            "sequenceEnd",
            "possessionTypeName",
            "xA",
        ]

        return final_third_entries[columns]

    except Exception as e:
        logger.error(f"Error getting final third entries: {e}")
        raise e

def analyze_entry_zones(events_df, team_id):
    """
    Analyse final third entries per zone
    
    Parameters:
    -----------
    events_df: pd.DataFrame
        The events dataframe.
    team_id: int
        The id of the team.
    
    Returns:
    --------
    pd.DataFrame
        The dataframe with the entries per zone and outcomes.
    """
    try:
        # Filter op final third entries (afhankelijk van je event types)
        # Dit kan zijn: carries into final third, passes into final third, etc.
        
        # Optie 1: Als je expliciet "final third entry" events hebt
        entries = events_df[
            (events_df['team_id'] == team_id) &
            (events_df['event_type'].isin(['carry', 'pass'])) &
            (events_df['end_x'] >= 17.5) &  # eindigt in final third
            (events_df['x'] < 17.5)  # begint ervoor
        ].copy()
        
        # Optie 2: Als je dit moet afleiden uit passes/carries
        # entries = find_entries_from_actions(events_df, team_id)
        
        # Classificeer zone
        entries['entry_zone'] = entries.apply(
            lambda row: classify_entry_zone(row['end_x'], row['end_y']), 
            axis=1
        )
        
        # Analyseer wat er na entry gebeurde
        entries['outcome'] = entries.apply(
            lambda row: analyze_sequence_outcome(events_df, row.name), 
            axis=1
        )
        return entries
    except Exception as e:
        logger.error(f"Error analyzing entry zones: {e}")
        raise e

def classify_entry_zone(x, y):
    """
    Classificeer final third entry in zone
    
    Parameters:
    - x, y: coördinaten van entry
    
    Returns:
    - zone name: 'left', 'center', 'right'
    """
    # Final third begint bij x = 17.5
    if x < 17.5:
        return None  # Nog geen final third
    
    # Horizontaal: links/centrum/rechts
    if y < -12:
        return 'left'
    elif y > 12:
        return 'right'
    else:
        return 'center'

def analyze_sequence_outcome(events_df, entry_idx, lookforward=10):
    """
    Bepaal wat er gebeurde na een final third entry
    
    Parameters:
    - events_df: alle events
    - entry_idx: index van entry event
    - lookforward: hoeveel events vooruit kijken
    
    Returns:
    - dict met outcome info
    """
    
    # Kijk naar volgende X events van hetzelfde team
    entry_event = events_df.loc[entry_idx]
    team_id = entry_event['team_id']
    timestamp = entry_event['timestamp']
    
    # Volgende events binnen 15 seconden van hetzelfde team
    next_events = events_df[
        (events_df.index > entry_idx) &
        (events_df['timestamp'] <= timestamp + 15) &
        (events_df['team_id'] == team_id)
    ].head(lookforward)
    
    outcome = {
        'shot': False,
        'goal': False,
        'xG': 0,
        'turnover': False,
        'foul_won': False,
        'corner': False,
        'end_reason': 'unknown'
    }
    
    for _, event in next_events.iterrows():
        if event['event_type'] == 'shot':
            outcome['shot'] = True
            outcome['xG'] = event.get('xG', 0)
            if event.get('outcome') == 'goal':
                outcome['goal'] = True
            outcome['end_reason'] = 'shot'
            break
        elif event['event_type'] in ['interception', 'tackle']:
            outcome['turnover'] = True
            outcome['end_reason'] = 'turnover'
            break
        elif event['event_type'] == 'foul':
            outcome['foul_won'] = True
            outcome['end_reason'] = 'foul_won'
            break
    
    # Check of er een event van andere team is (= balverlies)
    opponent_event = events_df[
        (events_df.index > entry_idx) &
        (events_df['timestamp'] <= timestamp + 15) &
        (events_df['team_id'] != team_id)
    ].head(1)
    
    if len(opponent_event) > 0 and not outcome['shot']:
        outcome['turnover'] = True
        outcome['end_reason'] = 'lost_possession'
    
    return outcome

def summarize_entries_by_zone(entries_df):
    """
    Maak samenvatting per zone
    """
    
    summary = entries_df.groupby('entry_zone').agg({
        'event_id': 'count',  # aantal entries
        'outcome': lambda x: sum([o['shot'] for o in x]),  # aantal shots
    }).rename(columns={'event_id': 'entries', 'outcome': 'shots'})
    
    # xG per zone
    summary['total_xG'] = entries_df.groupby('entry_zone')['outcome'].apply(
        lambda x: sum([o['xG'] for o in x])
    )
    
    summary['xG_per_entry'] = summary['total_xG'] / summary['entries']
    summary['shot_rate'] = summary['shots'] / summary['entries']
    
    # Turnovers
    summary['turnovers'] = entries_df.groupby('entry_zone')['outcome'].apply(
        lambda x: sum([o['turnover'] for o in x])
    )
    summary['turnover_rate'] = summary['turnovers'] / summary['entries']
    
    return summary