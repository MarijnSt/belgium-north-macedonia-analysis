from pathlib import Path
from typing import Tuple
import json
import logging
import pandas as pd

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

            self.event_data = pd.DataFrame(json_data['data'])
            self.player_data = pd.DataFrame(json_data['players'])

            logger.info(f"✓ Loaded {len(self.event_data)} events from {event_file}")
            logger.info(f"✓ Loaded {len(self.player_data)} players from {event_file}")

            return self.event_data, self.player_data
        
        except Exception as e:
            logger.error(f"Error loading event data: {e}")
            raise e