"""Configuration for styling."""

from pathlib import Path
from matplotlib import font_manager
from typing import Dict
import logging

# Get logger (initialized in source file)
logger = logging.getLogger(__name__)

class StylingConfig:
    @staticmethod
    def _load_fonts() -> Dict:
        """Load custom fonts from static directory."""
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        font_base_path = project_root / 'static' / 'fonts'
        
        font_paths = {
            'light': font_base_path / 'Futura-Light.ttf',
            'medium': font_base_path / 'Futura-Medium.ttf',
            'medium_italic': font_base_path / 'Futura-MediumItalic.ttf',
            'bold': font_base_path / 'Futura-Bold.ttf',
            'condensed_medium': font_base_path / 'Futura-CondensedMedium.ttf',
            'condensed_bold': font_base_path / 'Futura-CondensedExtraBold.ttf',
        }

        fonts = {}

        for name, path in font_paths.items():
            if path.exists():
                try:
                    font_manager.fontManager.addfont(str(path))
                    fonts[name] = font_manager.FontProperties(fname=str(path))
                except Exception as e:
                    logger.error(f"Failed to load font {name}: {e}")
            else:
                logger.error(f"Font {path} does not exist!")

        return fonts

    # Custom fonts
    fonts = _load_fonts()

    # Theme colors
    colors = {
        "primary": "#053225",
        "light": "#f2f4ee",
        "mkd_color": "#DC851F",
        "bel_color": "#C33C54",
    }

    # Alpha
    alpha = 0.2

    # Typography
    typo = {
        'sizes': {
            'h0': 40,
            'h1': 25,
            'h2': 18,
            'h3': 16,
            'p': 12,
            'label': 8,
        },
    }

    # Pitch
    pitch = {
        'pitch_type': "statsbomb",
        'line_color': colors['primary'],
        'linewidth': 0.5,
        'half': False,
        'goal_type': 'box',
        'corner_arcs': True,
        'pad_bottom': 0.1,
    }

    # Arrows
    arrows = {
        'width': 1,
        'headwidth': 5,
        'headlength': 5,
    }

styling = StylingConfig()