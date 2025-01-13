"""Configuration module for Uncluttr."""

import os
import sys

def get_base_app_files_path():
    """Get the base path for configuration files."""
    if getattr(sys, 'frozen', False):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        return sys._MEIPASS
    return os.getcwd()
