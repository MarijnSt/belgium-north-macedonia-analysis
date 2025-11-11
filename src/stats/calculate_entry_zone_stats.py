def calculate_entry_zone_stats(entries_df):
    """
    Create summary statistics per zone
    
    Parameters:
    -----------
    entries_df: pd.DataFrame
        DataFrame with all entries and their outcomes
    
    Returns:
    --------
    pd.DataFrame
        Summary statistics grouped by entry zone
    """
    
    # Basic aggregation
    summary = entries_df.groupby('entry_zone').agg({
        'eventId': 'count',  # Total entries
        'shot': 'sum',  # Count of entries that led to at least one shot
        'shot_count': 'sum',  # Total number of shots
        'box_entry': 'sum',  # Count of entries that led to at least one box entry
        'box_entry_count': 'sum',  # Total number of box entries
        'total_xg': 'sum',  # Total xG across all shots
        'turnover': 'sum',  # Count of entries that ended in turnover
        'recycled': 'sum',  # Count of entries that were recycled
    }).rename(columns={
        'eventId': 'total_entries',
        'shot': 'entries_with_shot',
        'shot_count': 'total_shots',
        'box_entry': 'entries_with_box_entry',
        'box_entry_count': 'total_box_entries',
        'total_xg': 'total_xg',
        'turnover': 'total_turnovers',
        'recycled': 'total_recycles'
    })
    
    # Calculate rates (based on entries, not counts)
    summary['shot_rate'] = (summary['entries_with_shot'] / summary['total_entries'])*100
    summary['box_entry_rate'] = (summary['entries_with_box_entry'] / summary['total_entries'])*100
    summary['turnover_rate'] = (summary['total_turnovers'] / summary['total_entries'])*100
    summary['recycle_rate'] = (summary['total_recycles'] / summary['total_entries'])*100
    
    # Calculate xG metrics
    summary['xg_per_entry'] = summary['total_xg'] / summary['total_entries']
    summary['xg_per_shot'] = summary['total_xg'] / summary['total_shots'].replace(0, float('nan'))  # Avoid division by zero
    
    # Reorder columns for readability
    column_order = [
        'total_entries',
        'entries_with_shot', 'total_shots', 'shot_rate',
        'total_xg', 'xg_per_entry', 'xg_per_shot',
        'entries_with_box_entry', 'total_box_entries', 'box_entry_rate',
        'total_turnovers', 'turnover_rate',
        'total_recycles', 'recycle_rate'
    ]
    
    return summary[column_order].reset_index()