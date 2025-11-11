"""Module for configuring the project."""

from .logging import setup_logging
from .styling import styling
from .config import PitchZones

__all__ = [
    "setup_logging",
    "styling",
    "PitchZones"
]