"""
Main module for the OneNote Excel Updater.

This script coordinates the process of reading Excel data and updating OneNote.
"""

import os
import logging
import sys
from datetime import datetime

from excel_reader import ExcelReader, DataProcessingError
from onenote_updater import OneNoteUpdater, BrowserAutomationError
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"onenote_updater_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)


def ensure_data_directory():
    """Create the data directory if it doesn't exist."""
    data_dir = os.path.dirname(config.EXCEL_FILE_PATH)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        logger.info(f"Created data directory: {data_dir}")


def main():
    """Main function to orchestrate the update process."""
    logger.info("Starting OneNote Excel Updater")
    
    # Ensure data directory exists
    ensure_data_directory()
    
    # Initialize the Excel reader
    try:
        logger.info(f"Reading Excel data from {config.EXCEL_FILE_PATH}")
        excel_reader = ExcelReader()
        excel_reader.read_data()
        
        # Get formatted data for OneNote
        formatted_data = excel_reader.get_formatted_data()
        logger.info(f"Successfully processed Excel data for date: {formatted_data['date']}")
        
    except DataProcessingError as e:
        logger.error(f"Error processing Excel data: {str(e)}")
        return
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        return
    
    # Use context manager for OneNote updater to ensure proper resource cleanup
    try:
        logger.info("Starting browser and navigating to OneNote")
        with OneNoteUpdater() as onenote_updater:
            # Open the specified notebook
            onenote_updater.open_notebook()
            
            # Update OneNote with Excel data
            logger.info("Updating OneNote with Excel data")
            onenote_updater.update_from_excel_data(formatted_data)
            
            logger.info("OneNote update completed successfully")
            
    except BrowserAutomationError as e:
        logger.error(f"Error updating OneNote: {str(e)}")
        return


if __name__ == "__main__":
    main()
