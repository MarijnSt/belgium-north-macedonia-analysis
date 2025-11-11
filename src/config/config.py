from dataclasses import dataclass
from typing import Dict, Tuple, Optional

class PitchZones:
    """
    Configuration class for pitch zones.
    """

    # Define pitch zones
    ZONES = {
        # Middle third: progression zone
        'left_progression': {'x': [-17.5, 17.5], 'y': [12, 34]},
        'center_progression': {'x': [-17.5, 17.5], 'y': [-12, 12]},
        'right_progression': {'x': [-17.5, 17.5], 'y': [-34, -12]},
        
        # Final third
        'left_final_third': {'x': [17.5, 52.5], 'y': [12, 34]},
        'center_final_third': {'x': [17.5, 52.5], 'y': [-12, 12]},
        'right_final_third': {'x': [17.5, 52.5], 'y': [-34, -12]},
    }

    @classmethod
    def get_zones(cls) -> dict:
        """
        Return the zones dictionary.
        """
        return cls.ZONES
    
    @classmethod
    def get_zone_for_position(cls, x: float, y: float) -> str:
        """
        Get the zone name for a given ball position.
        Returns 'build_up_zone' if position doesn't match any defined zone.
        """
        for zone_name, coords in cls.ZONES.items():
            x_min, x_max = coords['x']
            y_min, y_max = coords['y']
            
            if x_min <= x <= x_max and y_min <= y <= y_max:
                return zone_name
        
        return 'build_up_zone'
    
    @classmethod
    def get_zone_boundaries(cls, zone_name: str) -> Optional[Dict]:
        """Get the boundaries for a specific zone."""
        return cls.ZONES.get(zone_name)
    
    # @classmethod
    # def get_all_zone_names(cls) -> list:
    #     """Return list of all zone names including build_up_zone."""
    #     return list(cls.ZONES.keys()) + ['build_up_zone']