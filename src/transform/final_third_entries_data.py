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