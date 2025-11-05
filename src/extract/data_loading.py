from pathlib import Path
from typing import Tuple, Dict
import json
import logging
import pandas as pd
import pickle

# Get logger (initialized in source file)
logger = logging.getLogger(__name__)

class MatchDataLoader:
    """
    Handles loading and initial processing of match data files.
    """

    def __init__(self, game_dir: str = "../data/20251010-Belgium-North-Macedonia") -> None:
        """
        Init the data loader with the directory of the game.

        Parameters:
        -----------
        game_dir: str
            The directory of the game.
        """

        self.game_dir = Path(game_dir)
        self.event_data = None
        self.player_data = None
        self.tracking_data = None
        self.mapping_data = None

    def load_event_and_player_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load the event and player data from the events.json files into dataframes.

        Returns:
        --------
        event_df: pd.DataFrame
            The dataframe containing the event data.
        player_df: pd.DataFrame
            The dataframe containing the player data.
        """
        try:
            # Find the event.json file
            event_file = self.game_dir / "events.json"
            if not event_file.exists():
                raise FileNotFoundError(f"Event data file not found at {event_file}")

            # Load the event data
            with open(event_file, "r") as f:
                json_data = json.load(f)

            if json_data is None:
                raise ValueError("No data found in the event.json file")

            # Save data in class attributes as dataframes
            self.event_data = pd.DataFrame(json_data['data'])
            self.player_data = pd.DataFrame(json_data['players'])

            logger.info(f"✓ Loaded {len(self.event_data)} events from {event_file}")
            logger.info(f"✓ Loaded {len(self.player_data)} players from {event_file}")

            return self.event_data, self.player_data
        
        except Exception as e:
            logger.error(f"Error loading event data: {e}")
            raise e

    def load_mapping_data(self) -> Dict:
        """
        Load the mapping data from the mapping.json file into a dictionary.

        Returns:
        --------
        mapping_data: Dict
            The dictionary containing the mapping data.
        """
        try:
            # Find the mapping.json file
            mapping_file = self.game_dir / "mapping.json"
            if not mapping_file.exists():
                raise FileNotFoundError(f"Mapping data file not found at {mapping_file}")

            # Load the mapping data
            with open(mapping_file, "r") as f:
                json_data = json.load(f)

            if json_data is None:
                raise ValueError("No data found in the mapping.json file")

            # Save data in class attributes as dictionary
            self.mapping_data = json_data

            logger.info(f"✓ Loaded mapping data from {mapping_file}")

            return self.mapping_data
        
        except Exception as e:
            logger.error(f"Error loading mapping data: {e}")
            raise e
            
    def load_tracking_data(self) -> pd.DataFrame:
        """
        Load the tracking data from the tracking.pkl file into a dataframe.

        Returns:
        --------
        tracking_df: pd.DataFrame
            The dataframe containing the tracking data.
        """
        try:
            # Find the tracking.json file
            tracking_file = self.game_dir / "tracking.pkl"
            if not tracking_file.exists():
                raise FileNotFoundError(f"Tracking data file not found at {tracking_file}")

            # Load the tracking data
            with open(tracking_file, "rb") as f:
                self.tracking_data = pickle.load(f)

            logger.info(f"✓ Loaded {len(self.tracking_data)} tracking entries from {tracking_file}")
            return self.tracking_data
        
        except Exception as e:
            logger.error(f"Error loading tracking data: {e}")
            raise e

    def load_all_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict]:
        """
        Convenience method to load all data at once.

        Returns:
        --------
        events_data: pd.DataFrame
            The dataframe containing the event data.
        player_data: pd.DataFrame
            The dataframe containing the player data.
        tracking_data: pd.DataFrame
            The dataframe containing the tracking data.
        mapping_data: Dict
            The dictionary containing the mapping data.
        """
        try:
            self.load_event_and_player_data()
            self.load_tracking_data()
            self.load_mapping_data()

            return self.event_data, self.player_data, self.tracking_data, self.mapping_data
        
        except Exception as e:
            logger.error(f"Error loading all data: {e}")
            raise e