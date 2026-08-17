"""
Test script to see the data output from excel_reader.py

This script creates an instance of ExcelReader, reads the Excel data,
and displays different views of the data to help understand what's available.
"""

import logging
from excel_reader import ExcelReader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def display_excel_data():
    """Read and display Excel data in different formats."""
    try:
        logger.info("Creating ExcelReader instance...")
        reader = ExcelReader()
        
        # 1. Read the raw DataFrame
        logger.info("Reading Excel data...")
        df = reader.read_data()
        
        # Display basic DataFrame info
        logger.info(f"DataFrame shape: {df.shape}")
        logger.info(f"DataFrame columns: {list(df.columns)}")
        
        # 2. Display first few rows
        print("\n===== FIRST 5 ROWS OF RAW DATA =====\n")
        print(df.head(5).to_string())
        
        # 3. Get and display formatted data
        print("\n===== FORMATTED DATA =====\n")
        formatted_data = reader.get_formatted_data()
        
        # Print date and title
        print(f"Date: {formatted_data['date']}")
        print(f"Title: {formatted_data['title']}")
        
        # Print first 2 records in a nice format
        print("\nSample Records (first 2):")
        for i, record in enumerate(formatted_data['records'][:2]):
            print(f"\nRecord {i+1}:")
            for key, value in record.items():
                print(f"  {key}: {value}")
        
        # 4. Get and display summary
        print("\n===== DATA SUMMARY =====\n")
        summary = reader.get_summary()
        
        print(f"Row count: {summary['row_count']}")
        print(f"Columns: {', '.join(summary['columns'])}")
        
        if summary['numeric_summaries']:
            print("\nNumeric column statistics:")
            for column, stats in summary['numeric_summaries'].items():
                print(f"  {column}:")
                for stat_name, value in stats.items():
                    print(f"    {stat_name}: {value}")
        
        return True
    except Exception as e:
        logger.error(f"Error displaying Excel data: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n===== EXCEL READER DATA OUTPUT TEST =====\n")
    success = display_excel_data()
    
    if success:
        print("\nSuccessfully read and displayed Excel data!")
    else:
        print("\nFailed to read Excel data. Check the error logs.")
