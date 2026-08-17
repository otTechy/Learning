"""
Test script to see the data output from excel_reader with SharePoint authentication.

This script uses Playwright to authenticate to SharePoint and download the Excel file
before reading it with pandas.
"""

import logging
import os
import pandas as pd
from playwright.sync_api import sync_playwright
import tempfile
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def download_excel_from_sharepoint():
    """
    Download the Excel file from SharePoint using Playwright.
    
    Returns:
        Path to the downloaded file or None if failed.
    """
    temp_dir = tempfile.mkdtemp()
    
    logger.info(f"Temporary download directory: {temp_dir}")
    logger.info(f"Accessing SharePoint URL: {config.EXCEL_FILE_PATH}")
    
    with sync_playwright() as playwright:
        # Launch browser with downloads enabled
        browser = playwright.chromium.launch(headless=False)
        
        # Create browser context with downloads enabled
        context = browser.new_context(
            accept_downloads=True,
            viewport={'width': 1280, 'height': 800}
        )
        
        # Create new page
        page = context.new_page()
        
        try:
            # Navigate to SharePoint
            logger.info("Navigating to SharePoint...")
            page.goto(config.EXCEL_FILE_PATH, timeout=config.NAVIGATION_TIMEOUT)
            
            # Wait for authentication if needed (manual login)
            logger.info("Waiting for user to authenticate (if needed)...")
            
            # Wait for the page to load - look for Excel content or download option
            # This may vary depending on your SharePoint setup
            try:
                # Wait for Excel interface or download button to appear
                page.wait_for_selector("button, a[download], .ms-CommandBarItem-link", timeout=60000)
                logger.info("SharePoint page loaded successfully")
            except Exception as e:
                logger.warning(f"Timeout waiting for SharePoint page elements: {str(e)}")
                logger.info("Continuing anyway, page might still be usable...")
            
            # Look for and click a download button if available
            # This part may need to be customized based on your SharePoint interface
            try:
                logger.info("Looking for download option...")
                
                # Wait for user to navigate and possibly download the file
                # Allow 60 seconds for user to interact
                page.wait_for_timeout(60000)
                
                logger.info("If you've downloaded the file manually, please enter the file path when prompted.")
                
            except Exception as e:
                logger.error(f"Error finding or clicking download option: {str(e)}")
            
            context.close()
            browser.close()
            
            # Prompt user for file path if manually downloaded
            manual_file_path = input("\nIf you've downloaded the Excel file, enter the full path here: ")
            if manual_file_path and os.path.exists(manual_file_path):
                return manual_file_path
            else:
                logger.error("No valid file path provided")
                return None
                
        except Exception as e:
            logger.error(f"Error accessing SharePoint: {str(e)}")
            context.close()
            browser.close()
            return None

def display_excel_data(file_path):
    """Read and display Excel data from a downloaded file."""
    try:
        logger.info(f"Reading Excel file from: {file_path}")
        
        # Read the Excel file
        df = pd.read_excel(file_path, sheet_name=config.SHEET_NAME)
        
        # Display basic DataFrame info
        logger.info(f"DataFrame shape: {df.shape}")
        logger.info(f"DataFrame columns: {list(df.columns)}")
        
        # Display first few rows
        print("\n===== FIRST 5 ROWS OF RAW DATA =====\n")
        print(df.head(5).to_string())
        
        # Format current date (similar to the ExcelReader class)
        from datetime import datetime
        current_date = datetime.now().strftime(config.DATE_FORMAT)
        
        # Display what would be the formatted data
        print("\n===== FORMATTED DATA EXAMPLE =====\n")
        print(f"Date: {current_date}")
        print(f"Title: Update for {current_date}")
        
        # Print first 2 records in a nice format
        print("\nSample Records (first 2):")
        records = df.head(2).to_dict('records')
        for i, record in enumerate(records):
            print(f"\nRecord {i+1}:")
            for key, value in record.items():
                print(f"  {key}: {value}")
        
        # Display summary
        print("\n===== DATA SUMMARY =====\n")
        row_count = len(df)
        columns = list(df.columns)
        
        print(f"Row count: {row_count}")
        print(f"Columns: {', '.join(columns)}")
        
        # Calculate summaries for numeric columns
        numeric_columns = df.select_dtypes(include=['number']).columns
        if len(numeric_columns) > 0:
            print("\nNumeric column statistics:")
            for column in numeric_columns:
                print(f"  {column}:")
                print(f"    mean: {df[column].mean()}")
                print(f"    min: {df[column].min()}")
                print(f"    max: {df[column].max()}")
        
        return True
    except Exception as e:
        logger.error(f"Error displaying Excel data: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n===== SHAREPOINT EXCEL READER TEST =====\n")
    print("This script will open a browser window to authenticate to SharePoint.")
    print("You may need to log in manually if prompted.")
    print("You might need to download the Excel file manually if the download button isn't automatically detected.")
    
    # Download Excel file from SharePoint
    excel_file_path = download_excel_from_sharepoint()
    
    if excel_file_path:
        # Display Excel data
        success = display_excel_data(excel_file_path)
        
        if success:
            print("\nSuccessfully read and displayed Excel data!")
        else:
            print("\nFailed to read Excel data. Check the error logs.")
    else:
        print("\nFailed to download Excel file from SharePoint.")
