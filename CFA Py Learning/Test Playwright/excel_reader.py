"""
Excel reader module for the OneNote Excel Updater.

This module handles reading and processing data from Excel files using pandas.
"""

import pandas as pd
from datetime import datetime
import os
import logging
from typing import Dict, List, Any, Union
from abc import ABC, abstractmethod

import config

# Configure logging
logger = logging.getLogger(__name__)


class DataProcessingError(Exception):
    """Custom exception for data processing errors."""
    pass


class DataReader(ABC):
    """Abstract base class for data readers."""
    
    def __init__(self, file_path: str):
        """
        Initialize the data reader.
        
        Args:
            file_path: Path to the data file.
        """
        self.file_path = file_path
        self.data = None
    
    @abstractmethod
    def read_data(self):
        """Read data from the file. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_formatted_data(self):
        """Process and format data. Must be implemented by subclasses."""
        pass
    
    def validate_file_exists(self):
        """
        Validate that the file exists.
        
        Raises:
            FileNotFoundError: If the file does not exist.
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")


class ExcelReader(DataReader):
    """Class for reading and processing Excel data."""

    def __init__(self, file_path: str = None, sheet_name: str = None):
        """
        Initialize the ExcelReader.

        Args:
            file_path: Path to the Excel file. Defaults to the path in config.
            sheet_name: Name of the sheet to read. Defaults to the sheet in config.
        """
        super().__init__(file_path or config.EXCEL_FILE_PATH)
        self.sheet_name = sheet_name or config.SHEET_NAME

    def read_excel(self) -> pd.DataFrame:
        """
        Read data from the Excel file.

        Returns:
            DataFrame containing the Excel data.
        
        Raises:
            DataProcessingError: If there are issues with the Excel data.
        """
        try:
            self.validate_file_exists()
            
            self.data = pd.read_excel(self.file_path, sheet_name=self.sheet_name)
            
            # Basic validation
            if self.data.empty:
                raise ValueError("Excel file contains no data")
                
            return self.data
            
        except Exception as e:
            raise DataProcessingError(f"Error reading Excel file: {str(e)}")
    
    def read_data(self) -> pd.DataFrame:
        """
        Read data from the Excel file. Implementation of abstract method.
        
        Returns:
            DataFrame containing the Excel data.
        """
        return self.read_excel()

    def get_formatted_data(self) -> Dict[str, Union[str, List[Dict[str, Any]]]]:
        """
        Process and format the Excel data for OneNote.

        Returns:
            Dictionary with date as key and formatted data as value.
        """
        if self.data is None:
            self.read_excel()
            
        # Format the current date for the section name
        current_date = datetime.now().strftime(config.DATE_FORMAT)
        
        # Process data as needed
        # This is a simple example; modify according to your specific data structure
        formatted_data = {
            "date": current_date,
            "title": f"Update for {current_date}",
            "records": self.data.to_dict('records')
        }
        
        return formatted_data

    def get_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of the Excel data.

        Returns:
            Dictionary with summary statistics.
            
        Raises:
            DataProcessingError: If summary generation fails.
        """
        try:
            if self.data is None:
                self.read_data()
                
            summary = {
                "row_count": len(self.data),
                "columns": list(self.data.columns),
                "numeric_summaries": {}
            }
            
            # Add summaries for numeric columns
            for column in self.data.select_dtypes(include=['number']).columns:
                summary["numeric_summaries"][column] = {
                    "mean": self.data[column].mean(),
                    "min": self.data[column].min(),
                    "max": self.data[column].max()
                }
                
            return summary
        except Exception as e:
            raise DataProcessingError(f"Error generating data summary: {str(e)}")


class CSVReader(DataReader):
    """Class for reading and processing CSV data. Example of extending the DataReader."""
    
    def __init__(self, file_path: str = None, delimiter: str = ','):
        """
        Initialize the CSVReader.
        
        Args:
            file_path: Path to the CSV file.
            delimiter: CSV delimiter character.
        """
        super().__init__(file_path or "data/sample.csv")
        self.delimiter = delimiter
    
    def read_data(self) -> pd.DataFrame:
        """
        Read data from the CSV file.
        
        Returns:
            DataFrame containing the CSV data.
        """
        try:
            self.validate_file_exists()
            
            self.data = pd.read_csv(self.file_path, delimiter=self.delimiter)
            
            # Basic validation
            if self.data.empty:
                raise ValueError("CSV file contains no data")
                
            return self.data
            
        except Exception as e:
            raise DataProcessingError(f"Error reading CSV file: {str(e)}")
    
    def get_formatted_data(self) -> Dict[str, Union[str, List[Dict[str, Any]]]]:
        """
        Process and format the CSV data.
        
        Returns:
            Dictionary with formatted data.
        """
        if self.data is None:
            self.read_data()
            
        # Format the current date for the section name
        current_date = datetime.now().strftime(config.DATE_FORMAT)
        
        # Process data as needed
        formatted_data = {
            "date": current_date,
            "title": f"CSV Update for {current_date}",
            "records": self.data.to_dict('records')
        }
        
        return formatted_data
