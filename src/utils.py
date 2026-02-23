"""Utility functions for folder creation and common operations."""
from pathlib import Path


def create_folders():
    """Create all required folders if they don't exist."""
    folders = ['data', 'bronze', 'silver', 'gold', 'visualizations']
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)
