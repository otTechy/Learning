"""
Utility functions for the OneNote Excel Updater.
"""

import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def format_date(date_str=None, format_str="%Y-%m-%d"):
    """
    Format a date string or return today's date if none provided.
    
    Args:
        date_str: Date string to format. If None, today's date is used.
        format_str: Format string for the output date.
        
    Returns:
        Formatted date string.
    """
    if date_str:
        try:
            # Try to parse the provided date string
            # This assumes ISO format (YYYY-MM-DD) but could be modified
            date_obj = datetime.fromisoformat(date_str.split('T')[0])
        except (ValueError, AttributeError):
            logger.warning(f"Invalid date format: {date_str}. Using today's date instead.")
            date_obj = datetime.now()
    else:
        date_obj = datetime.now()
        
    return date_obj.strftime(format_str)


def sanitize_filename(filename):
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename: The filename to sanitize.
        
    Returns:
        Sanitized filename.
    """
    # Replace characters that are invalid in filenames
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def get_latest_file(directory, pattern=None):
    """
    Get the most recently modified file in a directory.
    
    Args:
        directory: Directory to search.
        pattern: Optional pattern to filter files.
        
    Returns:
        Path to the most recently modified file, or None if no files match.
    """
    if not os.path.exists(directory):
        logger.warning(f"Directory does not exist: {directory}")
        return None
        
    files = os.listdir(directory)
    
    if pattern:
        files = [f for f in files if pattern in f]
        
    if not files:
        logger.warning(f"No files found in {directory}" + 
                      (f" matching pattern '{pattern}'" if pattern else ""))
        return None
        
    files = [os.path.join(directory, f) for f in files]
    files.sort(key=os.path.getmtime, reverse=True)
    
    return files[0]
