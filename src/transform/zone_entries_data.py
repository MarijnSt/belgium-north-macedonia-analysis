import pandas as pd
import logging

logger = logging.getLogger(__name__)

def get_zone_entries_data(
    final_third_entries_df: pd.DataFrame, 
    events_df: pd.DataFrame,
    team_name: str
) -> pd.DataFrame:
    """
    Get the zone entries data.
    
    Parameters:
    -----------
    final_third_entries_df: pd.DataFrame
        The final third entries dataframe.
    events_df: pd.DataFrame
        The events dataframe of the game.
    team_name: str
        The name of the team.
    
    Returns:
    --------
    pd.DataFrame
        The dataframe with the zone entries data.
    """
    try:
        # Get final third entries for team
        entries_df = final_third_entries_df[final_third_entries_df["teamName"] == team_name].copy()
        logger.debug(f"Entries for {team_name}: {len(entries_df)}")
        
        # Classify zone
        entries_df["entry_zone"] = entries_df.apply(
            lambda row: classify_entry_zone(row["endPosXM"], row["endPosYM"]), 
            axis=1
        )

        
        # Analyze what happened after the entry
        entries_df['outcome'] = entries_df.apply(
            lambda row: analyze_sequence_outcome(
                team_name,
                events_df, 
                row["sequenceId"],
                row["eventId"],
                row["timestamp"]
            ), 
            axis=1
        )

        # Split outcome into separate columns
        outcome_cols = ['box_entry', 'box_entry_count', 'shot', 'shot_count', 'goal', 'goal_count', 'total_xg', 'turnover', 'recycled']
        for col in outcome_cols:
            entries_df[col] = entries_df['outcome'].apply(lambda x: x[col])
        # entries_df.drop(columns=['outcome'], inplace=True)

        return entries_df
    except Exception as e:
        logger.error(f"Error analyzing entry zones: {e}")
        raise e

def classify_entry_zone(x, y):
    """
    Classify final third entry zone
    
    Parameters:
    -----------
    x: float
        The x coordinate of the entry.
    y: float
        The y coordinate of the entry.
    
    Returns:
    --------
    str
        The name of the entry zone.
    """
    # Final third starts at x = 17.5
    if x < 17.5:
        return None  # No final third
    
    # Horizontal: left/center/right
    if y < -12:
        return "right"
    elif y > 12:
        return "left"
    else:
        return "center"

def analyze_sequence_outcome(team_name, events_df, sequence_id, entry_event_id, entry_timestamp, time_window=15000):
    """
    Analyze the outcome of a sequence after the entry event
    
    Parameters:
    -----------
    team_name: str
        The name of the team.
    events_df: pd.DataFrame
        The events dataframe of the game.
    sequence_id: int
        The id of the sequence.
    entry_event_id: int
        The id of the entry event.
    entry_timestamp: int
        The timestamp of the entry event.
    time_window: int
        The time window in milliseconds to look forward.
    
    Returns:
    --------
    outcome: dict
        The outcome of the sequence.
        - box_entry: bool
        - shot: bool
        - shot_count: int
        - goal: bool
        - goal_count: int
        - total_xg: float
        - turnover: bool
        - recycled: bool
    """
    try:
        # Init outcome object
        outcome = {
            "box_entry": False,
            "box_entry_count": 0,
            "shot": False,
            "shot_count": 0,
            "goal": False,
            "goal_count": 0,
            "total_xg": 0,
            "turnover": False,
            "recycled": False,
        }

        # Get events in the time window after the entry event
        next_events = events_df[
            (events_df["sequenceId"] == sequence_id) &
            (events_df["timestamp"] >= entry_timestamp) &
            (events_df["timestamp"] <= entry_timestamp + time_window)
        ].sort_values(by="timestamp")

        # Check if there's another entry event in the time window
        another_entry = next_events[
            (next_events["eventId"] != entry_event_id) &
            (next_events["startPosXM"] < 17.5) &
            (next_events["endPosXM"] >= 17.5)
        ]

        # If there's another entry in the time window:
        # - Set recycled to True
        # - Adapt next events to only include events before the recycled entry
        if len(another_entry) > 0:
            outcome["recycled"] = True
            recycled_entry = another_entry.iloc[0]
            recycled_entry_timestamp = recycled_entry["timestamp"]
            next_events = next_events[next_events["timestamp"] < recycled_entry_timestamp]

        # Init list for counting certain events
        box_entries_found = []
        shots_found = []

        # Loop through next events and check for other outcomes
        for _, event in next_events.iterrows():
            # Check for turnovers first (ends the loop)
            if event['baseTypeName'] in ['INTERCEPTION', 'CLEARANCE'] and event['teamName'] != team_name:
                outcome['turnover'] = True
                break

            # Check for box entries
            if is_box_entry(event):
                box_entries_found.append(event["eventId"])

            # Check for shots
            if event['baseTypeName'] == 'SHOT':
                shot_xg = event["metrics"]["xG"]
                is_goal = event["resultId"] == 1
                
                shots_found.append({
                    "xG": shot_xg,
                    "goal": is_goal
                })
        
        # Aggregate box entry information
        if len(box_entries_found) > 0:
            outcome['box_entry'] = True
            outcome['box_entry_count'] = len(box_entries_found)

        # Aggregate shot information
        if len(shots_found) > 0:
            outcome["shot"] = True
            outcome["shot_count"] = len(shots_found)
            outcome["total_xg"] = sum([shot["xG"] for shot in shots_found])
            outcome["goal"] = any([shot["goal"] for shot in shots_found])
            outcome["goal_count"] = sum([shot["goal"] for shot in shots_found])
        
        return outcome
    
    except Exception as e:
        logger.error(f"Error analyzing sequence outcome: {e}")
        raise e

def is_box_entry(event):
    """
    Check if an event represents a box entry
    A box entry is when the ball goes from outside to inside the penalty box
    
    Box coordinates:
    - X: 36 <= X <= 52.5 (16.5m deep box)
    - Y: -20.16 <= Y <= 20.16 (40.32m wide box)

    Parameters:
    -----------
    event: Series
        The event to check.
    
    Returns:
    --------
    bool
        True if the event represents a box entry, False otherwise.
    """
    # Get start and end positions
    start_x = event["startPosXM"]
    start_y = event["startPosYM"]
    end_x = event["endPosXM"]
    end_y = event["endPosYM"]
    
    # Check if started inside the box
    started_inside = (
        36 <= start_x <= 52.5 and 
        -20.16 <= start_y <= 20.16
    )
    
    # Check if ended inside the box
    ended_inside = (
        36 <= end_x <= 52.5 and 
        -20.16 <= end_y <= 20.16
    )
    
    # Box entry: started outside, ended inside
    return (not started_inside) and ended_inside
