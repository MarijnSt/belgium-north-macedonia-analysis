import logging
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import pandas as pd

from config import styling

# Get logger (initialized in source file)
logger = logging.getLogger(__name__)

def plot_tracking_frame(tracking_df: pd.DataFrame, frame_id: int):
    """
    Plot a tracking frame.
    """
    try:
        # Init plt styling
        plt.rcParams.update({
            'font.family': styling.fonts['light'].get_name(),
            'font.size': styling.typo['sizes']['p'],
            'text.color': styling.colors['primary'],
            'axes.labelcolor': styling.colors['primary'],
            'axes.edgecolor': styling.colors['primary'],
            'xtick.color': styling.colors['primary'],
            'ytick.color': styling.colors['primary'],
            'grid.color': styling.colors['primary'],
            'figure.facecolor': styling.colors['light'],
            'axes.facecolor': styling.colors['light'],
        })

        pitch = Pitch(
            pitch_type=styling.pitch['pitch_type'],
            pitch_length=styling.pitch['pitch_length'],
            pitch_width=styling.pitch['pitch_width'],
            line_color=styling.pitch['line_color'], 
            linewidth=styling.pitch['linewidth'], 
            goal_type=styling.pitch['goal_type'], 
            corner_arcs=styling.pitch['corner_arcs'],
        )

        fig, ax = pitch.draw()

        # Get the frame data
        frame = tracking_df[tracking_df['frame_id'] == frame_id].iloc[0]

        # Extract and plot home players (blue)
        home_cols = [col for col in tracking_df.columns if col.startswith('home_') and col.endswith('_x')]
        for col in home_cols:
            x_col = col
            y_col = col.replace('_x', '_y')
            
            x = frame[x_col]
            y = frame[y_col]
            
            # Only plot if coordinates are not NaN
            if pd.notna(x) and pd.notna(y):
                pitch.scatter(x, y, c=styling.colors['bel_color'], s=100, linewidth=1, ax=ax)
        
        # Extract and plot away players (red)
        away_cols = [col for col in tracking_df.columns if col.startswith('away_') and col.endswith('_x')]
        for col in away_cols:
            x_col = col
            y_col = col.replace('_x', '_y')
            
            x = frame[x_col]
            y = frame[y_col]
            
            # Only plot if coordinates are not NaN
            if pd.notna(x) and pd.notna(y):
                pitch.scatter(x, y, c=styling.colors['mkd_color'], s=100, linewidth=1, ax=ax)
        
        # Plot the ball (green)
        ball_x = frame['ball_x']
        ball_y = frame['ball_y']
        if pd.notna(ball_x) and pd.notna(ball_y):
            pitch.scatter(ball_x, ball_y, c=styling.colors['primary'], s=50, linewidth=1, ax=ax, zorder=10)

        logger.info(f"Frame {frame_id} plotted")
        logger.info(f"Ball x: {ball_x}, Ball y: {ball_y}")

        # return fig
    except Exception as e:
        logger.error(f"Error plotting tracking frame: {e}")
        raise e