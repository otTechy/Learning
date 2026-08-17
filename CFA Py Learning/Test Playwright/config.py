"""
Configuration settings for the OneNote Excel Updater.

This module contains all the configuration parameters needed for the application,
including file paths, OneNote URLs, and authentication settings.
"""

# Excel file settings
EXCEL_FILE_PATH = "https://secbenefit.sharepoint.com/:x:/r/investments/Derivatives/_layouts/15/Doc.aspx?sourcedoc=%7BE93D047E-0387-4C57-97B6-9760F8356739%7D&file=Jira_Tracker.xlsm&action=default&mobileredirect=true"
SHEET_NAME = "Jira DWC In Progress_Quant"

# Authentication settings
EMAIL = "shujing.purcell@securitybenefit.com"  # Email for authentication
# PASSWORD should be entered manually for security

# OneNote settings
ONENOTE_URL = "https://secbenefit-my.sharepoint.com/personal/shujing_purcell_securitybenefit_com/_layouts/15/Doc.aspx?sourcedoc={425bcc85-8f3e-4e54-849b-87be4bc04633}&action=edit&wd=target%28Deriv%20Quant%2FQuant%20Standup%202025.one%7C6aa489d1-21d6-4faf-8708-379b2fdd123a%2F8%5C%2F18%5C%2F2025%7C28a166b5-9120-4659-9fac-ab9377848520%2F%29&wdorigin=NavigationUrl"
NOTEBOOK_NAME = "TestOneNote"  # Replace with your actual notebook name
SECTION_GROUP_NAME = "Quant Standup 2025"  # Replace with your actual section group name, if applicable

# Date format for creating new sections
DATE_FORMAT = "%#m/%#d/%Y"  # Example: 8/4/2025 (Windows format without leading zeros)
# Use "%-m/%-d/%Y" on Unix/Linux/Mac

# Browser settings
HEADLESS = False  # Set to True to run browser in headless mode

# Timeout settings (in milliseconds)
DEFAULT_TIMEOUT = 30000  # 30 seconds
NAVIGATION_TIMEOUT = 60000  # 60 seconds

# Login credentials (Consider using environment variables for security)
# USERNAME = "your_email@example.com"
# PASSWORD = "your_password"
