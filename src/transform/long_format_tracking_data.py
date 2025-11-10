import logging
import pandas as pd

logger = logging.getLogger(__name__)

def transform_tracking_to_long_format(tracking_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the tracking data to long format.

    Parameters:
    -----------
    tracking_df: pd.DataFrame
        The tracking dataframe to transform.

    Returns:
    --------
    pd.DataFrame
        The transformed dataframe.
    """
    try:
        # Base columns
        base_cols = ["frame_id", "period_id", "timestamp", "wall_clock", "ball_status", 
                    "last_touch", "ball_x", "ball_y", "ball_z", "ball_speed"]
        
        id_vars = [col for col in base_cols if col in tracking_df.columns]
        
        # Get all player columns
        player_cols = [col for col in tracking_df.columns if col not in base_cols]
        
        # Melt the data
        melted = tracking_df.melt(
            id_vars=id_vars,
            value_vars=player_cols,
            var_name="column",
            value_name="value"
        )
        
        # Drop NaN (players on the bench)
        melted = melted.dropna(subset=["value"])
        
        # Parse column names
        melted[["team_shirt", "property"]] = melted["column"].str.rsplit("_", n=1, expand=True)
        melted[["team_id", "shirt_number"]] = melted["team_shirt"].str.split("_", n=1, expand=True)
        
        # Pivot back to x, y, speed, id per player
        pivoted = melted.pivot_table(
            index=["frame_id", "period_id", "timestamp", "wall_clock", "team_id", "shirt_number", "last_touch"],
            columns="property",
            values="value",
            aggfunc="first"
        ).reset_index()
        
        # Remove the column name from the pivot to avoid concat issues
        pivoted.columns.name = None
        
        # # Rename columns
        # pivoted = pivoted.rename(columns={'id': 'player_id'})
        # Map team_id to team_name
        team_mapping = {
            "home": "Belgium",
            "away": "North Macedonia"
        }
        pivoted["team_name"] = pivoted["team_id"].map(team_mapping)
        
        # Add ball - only select columns that exist in both dataframes
        ball_cols = [col for col in id_vars if col not in ["ball_status", "ball_z"]]
        ball_data = tracking_df[ball_cols].copy()
        ball_data["team_name"] = "ball"
        ball_data["player_id"] = "ball"
        ball_data["shirt_number"] = 0
        ball_data = ball_data.rename(columns={"ball_x": "x", "ball_y": "y", "ball_speed": "speed"})
        
        # Combine
        result = pd.concat([pivoted, ball_data], ignore_index=True)
        
        # Clean up columns
        result["shirt_number"] = pd.to_numeric(result["shirt_number"], errors="coerce")

        # Map last_touch for all rows (both player and ball rows)
        result["last_touch"] = result["last_touch"].map(team_mapping)
        
        return result[["frame_id", "period_id", "timestamp", "wall_clock", 
                    "team_name", "shirt_number", "x", "y", "speed", "last_touch"]]

    except Exception as e:
        logger.error(f"Error transforming tracking data to long format: {e}")
        raise e