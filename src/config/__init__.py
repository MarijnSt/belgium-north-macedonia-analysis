"""Module for configuring the project."""

from .logging import setup_logging
from .styling import styling

__all__ = [
    'setup_logging',
    'styling'
]