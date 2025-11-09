import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

def get_passing_network_data(events_df, player_data, team_name):
    """
    Get the passing network data.

    Parameters:
    -----------
    events_df: pd.DataFrame
        The events dataframe of the game.
    player_data: pd.DataFrame
        The player dataframe of the game.

    Returns:
    --------
    scatter_df: pd.DataFrame
        The passing network data.
    lines_df: pd.DataFrame
        The passing network lines data.
    """
    try:
        # Check for first substitution
        sub_time = events_df[(events_df["baseTypeName"] == "SUBSTITUTE") & (events_df["teamName"] == team_name)].iloc[0]["timestamp"]

        # Get passes
        passes_df = events_df[
            (events_df["timestamp"] < sub_time) &
            (events_df["teamName"] == team_name) &
            (events_df["baseTypeName"] == "PASS") &
            (events_df["subTypeName"] != "THROW_IN") &
            (events_df["resultName"] == "SUCCESSFUL") &
            (events_df["receiverId"] != -1)
        ][["eventId", "startPosXM", "endPosXM", "startPosYM", "endPosYM", "playerId", "receiverId"]]

        # Add player shirt numbers
        passes_df["playerShirtNumber"] = passes_df["playerId"].map(player_data.set_index("playerId")["shirtNumber"])
        passes_df["receiverShirtNumber"] = passes_df["receiverId"].map(player_data.set_index("playerId")["shirtNumber"])

        # Calculate location and size of scatter points
        scatter_df = pd.DataFrame()
        for i, name in enumerate(passes_df["playerShirtNumber"].unique()):
            # Get the x and y coordinates for the passes and receptions
            pass_x = passes_df.loc[passes_df["playerShirtNumber"] == name]["startPosXM"].to_numpy()
            rec_x = passes_df.loc[passes_df["receiverShirtNumber"] == name]["endPosXM"].to_numpy()
            pass_y = passes_df.loc[passes_df["playerShirtNumber"] == name]["startPosYM"].to_numpy()
            rec_y = passes_df.loc[passes_df["receiverShirtNumber"] == name]["endPosYM"].to_numpy()
            scatter_df.at[i, "playerShirtNumber"] = name

            # Average the x and y coordinates for the passes and receptions
            scatter_df.at[i, "x"] = np.mean(np.concatenate([pass_x, rec_x]))
            scatter_df.at[i, "y"] = np.mean(np.concatenate([pass_y, rec_y]))

            # Calculate the number of passes
            scatter_df.at[i, "no"] = passes_df.loc[passes_df["playerShirtNumber"] == name].count().iloc[0]
        
        # Set marker size
        scatter_df['marker_size'] = (scatter_df['no'] / scatter_df['no'].max() * 1250)
        
        scatter_df["playerShirtNumber"] = scatter_df["playerShirtNumber"].astype(int)

        # Create line data
        # Count passes between players
        passes_df["pair_key"] = passes_df.apply(lambda x: "_".join(sorted([str(int(x["playerShirtNumber"])), str(int(x["receiverShirtNumber"]))])), axis=1)
        lines_df = passes_df.groupby(["pair_key"]).eventId.count().reset_index()
        lines_df.rename({'eventId':'pass_count'}, axis='columns', inplace=True)
        
        # Set passing treshold
        lines_df = lines_df[lines_df['pass_count'] > 2]

        return scatter_df, lines_df
    except Exception as e:
        logger.error(f"Error getting passing network data: {e}")
        raise e