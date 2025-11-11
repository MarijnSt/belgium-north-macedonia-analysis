import logging
import pandas as pd
import numpy as np
from scipy.spatial import ConvexHull

from config import PitchZones

logger = logging.getLogger(__name__)

def analyze_block_by_ball_position(
        tracking_df: pd.DataFrame, 
        defending_team_name: str = "North Macedonia", 
        possession_frame_ids: list[int] = None
) -> dict:
    """
    Analyse defensive block by ball position - FIXED AND OPTIMIZED VERSION.
    """
    try:
        if possession_frame_ids is None:
            logger.error("No possession frame ids provided")
            raise ValueError("No possession frame ids provided")

        if len(tracking_df) == 0:
            logger.error("No tracking dataframe provided")
            raise ValueError("No tracking dataframe provided")

        # Init zones
        zones = PitchZones.get_zones()

        # Sample frames (speed up analysis)
        sampled_frames = possession_frame_ids[::10]
        sampled_frames_set = set(sampled_frames)
        
        logger.info(f"Processing {len(sampled_frames)} sampled frames")
        
        # OPTIMIZATION 1: Pre-filter tracking data to only sampled frames
        tracking_filtered = tracking_df[tracking_df['frame_id'].isin(sampled_frames_set)].copy()
        
        logger.info(f"Filtered tracking data from {len(tracking_df)} to {len(tracking_filtered)} rows")
        
        # OPTIMIZATION 2: Set index for faster lookups
        tracking_filtered = tracking_filtered.set_index('frame_id')
        
        # OPTIMIZATION 3: Pre-extract ball data and defender data
        ball_data = tracking_filtered[tracking_filtered['team_name'] == 'ball'][['x', 'y']].copy()
        defender_data = tracking_filtered[tracking_filtered['team_name'] == defending_team_name].copy()
        
        # Add zone assignment to ball data vectorized
        def assign_zone_vectorized(row):
            for zone_name, coords in zones.items():
                x_min, x_max = coords['x']
                y_min, y_max = coords['y']
                if x_min <= row['x'] <= x_max and y_min <= row['y'] <= y_max:
                    return zone_name
            return 'build_up_zone'
        
        ball_data['zone'] = ball_data.apply(assign_zone_vectorized, axis=1)
        
        # OPTIMIZATION 4: Group defenders by frame_id once
        defender_groups = defender_data.groupby(level='frame_id')
        
        # Init results
        results = {zone_name: {
            'positions': [],
            'block_metrics': [],
            'frame_count': 0
        } for zone_name in list(zones.keys()) + ['build_up_zone']}
        
        # Process frames
        processed_count = 0
        for frame_id in sampled_frames:
            if frame_id not in ball_data.index:
                continue
            
            # Get ball zone
            zone = ball_data.loc[frame_id, 'zone']
            
            # Get defenders for this frame
            if frame_id not in defender_groups.groups:
                continue
                
            defenders = defender_groups.get_group(frame_id)
            
            if len(defenders) < 3:
                continue

            # Exclude goalkeeper from metrics calculation
            outfield_defenders = defenders[defenders['shirt_number'] != 23] # TODO: Make this dynamic (get goalkeeper shirt number from player data)

            if len(outfield_defenders) < 3:
                continue
            
            # Calculate metrics
            block_metrics = calculate_block_metrics(outfield_defenders)
            
            if block_metrics is None:
                continue
            
            # Save to zone results
            results[zone]['frame_count'] += 1
            results[zone]['block_metrics'].append(block_metrics)
            
            # OPTIMIZATION 5 + FIX: Save positions with player identifier (shirt_number)
            # Use vectorized operations instead of iterrows
            positions_list = defenders[['shirt_number', 'x', 'y']].to_dict('records')
            results[zone]['positions'].extend(positions_list)
            
            processed_count += 1
            
            # Progress logging every 1000 frames
            if processed_count % 1000 == 0:
                logger.info(f"Processed {processed_count}/{len(sampled_frames)} frames")
        
        logger.info(f"Finished processing {processed_count} frames")
        
        # Calculate averages per zone
        summary = {}
        
        for zone_name, data in results.items():
            if data['frame_count'] == 0:
                continue
            
            # Average positions per player - FIXED: group by shirt_number
            positions_df = pd.DataFrame(data['positions'])
            avg_positions = positions_df.groupby('shirt_number')[['x', 'y']].mean()
            
            # Average compactness metrics
            metrics_df = pd.DataFrame(data['block_metrics'])
            avg_metrics = metrics_df.mean().to_dict()
            
            summary[zone_name] = {
                'avg_positions': avg_positions,
                'avg_compactness': avg_metrics,
                'frame_count': data['frame_count']
            }
        
        return summary

    except Exception as e:
        logger.error(f"Error analyzing defensive block by ball position: {e}")
        raise e

def get_ball_position(tracking_df: pd.DataFrame, frame_id: int) -> dict:
    """Get the ball position for a given frame."""
    try:
        ball_data = tracking_df[
            (tracking_df['frame_id'] == frame_id) & 
            (tracking_df['team_name'] == 'ball')
        ]
        
        if len(ball_data) == 0:
            return None
        
        return {
            'x': ball_data['x'].iloc[0],
            'y': ball_data['y'].iloc[0]
        }
    except Exception as e:
        logger.error(f"Error getting ball position: {e}")
        raise e

def get_ball_zone(ball_x: float, ball_y: float, zones: dict) -> str:
    """Get the zone for a given ball position."""
    try:
        for zone_name, coords in zones.items():
            x_min, x_max = coords['x']
            y_min, y_max = coords['y']
            
            if x_min <= ball_x <= x_max and y_min <= ball_y <= y_max:
                return zone_name
        
        return 'build_up_zone'

    except Exception as e:
        logger.error(f"Error getting ball zone: {e}")
        raise e

def calculate_block_metrics(team_df: pd.DataFrame) -> dict:
    """Calculate the compactness metrics for a team at a given moment."""
    try:
        if len(team_df) < 3:
            return None
        
        points = team_df[['x', 'y']].values
        
        return {
            'area': calculate_convex_hull_area(points),
            'vertical_spread': team_df['x'].max() - team_df['x'].min(),
            'horizontal_spread': team_df['y'].max() - team_df['y'].min(),
            'mean_x': team_df['x'].mean(),
            'mean_y': team_df['y'].mean(),
            'defensive_line': team_df['x'].max(),
        }

    except Exception as e:
        logger.error(f"Error calculating team compactness: {e}")
        raise e

def calculate_convex_hull_area(points: np.ndarray) -> float:
    """Calculate the area of a convex hull."""
    try:
        if len(points) < 3:
            return None
        try:
            hull = ConvexHull(points)
            return hull.volume  # in 2D this is the area
        except:
            return None
    
    except Exception as e:
        logger.error(f"Error calculating convex hull area: {e}")
        raise e