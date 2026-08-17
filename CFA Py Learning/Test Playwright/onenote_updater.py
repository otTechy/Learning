"""
OneNote updater module for the OneNote Excel Updater.

This module handles interactions with OneNote using Playwright for web automation.
It can create new sections, pages and update content dynamically.
"""

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
import time
from datetime import datetime
from typing import Dict, List, Any, Union
import logging
from abc import ABC, abstractmethod

import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BrowserAutomationError(Exception):
    """Custom exception for browser automation errors."""
    pass


class WebAutomator(ABC):
    """Abstract base class for web automation with Playwright."""
    
    def __init__(self, headless: bool = None, timeout: int = None):
        """
        Initialize the web automator.
        
        Args:
            headless: Whether to run the browser in headless mode.
            timeout: Default timeout for actions in milliseconds.
        """
        self.headless = headless if headless is not None else config.HEADLESS
        self.timeout = timeout or config.DEFAULT_TIMEOUT
        
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    def __enter__(self):
        """Enable context manager protocol for automatic resource cleanup."""
        self.start_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when exiting context manager."""
        self.close()
        # Return False to propagate exceptions
        return False
    
    @abstractmethod
    def start_browser(self) -> None:
        """Launch the browser and configure it. Must be implemented by subclasses."""
        pass
    
    def close(self) -> None:
        """Close the browser and clean up resources."""
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
                
            logger.info("Browser closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
        finally:
            self.playwright = None
            self.browser = None
            self.context = None
            self.page = None


class OneNoteUpdater(WebAutomator):
    """Class for automating OneNote interactions using Playwright."""

    def __init__(self, headless: bool = None, timeout: int = None):
        """
        Initialize the OneNote updater.
        
        Args:
            headless: Whether to run the browser in headless mode.
            timeout: Default timeout for actions in milliseconds.
        """
        super().__init__(headless, timeout)

    def start_browser(self) -> None:
        """
        Launch the browser and navigate to OneNote.
        
        Raises:
            BrowserAutomationError: If browser initialization fails.
        """
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            self.page.set_default_timeout(self.timeout)
            
            # Navigate to OneNote
            logger.info(f"Navigating to OneNote at {config.ONENOTE_URL}")
            self.page.goto(config.ONENOTE_URL, timeout=config.NAVIGATION_TIMEOUT)
            
            # Wait for the page to load
            self.page.wait_for_load_state("networkidle")
            
            # Handle login if needed
            self._handle_login_if_needed()
            
        except Exception as e:
            self.close()
            raise BrowserAutomationError(f"Failed to start browser: {str(e)}")

    def _handle_login_if_needed(self) -> None:
        """
        Check if login is required and handle the authentication process.
        
        Note: This is a simplified example. Real implementation would depend on
        the actual OneNote login page structure and might require environment variables
        for credentials.
        """
        # Check if we're on a login page
        if self.page.url.startswith("https://login.microsoftonline.com") or "login" in self.page.url:
            logger.info("Login page detected, attempting to log in")
            
            # Uncomment and modify based on the actual login form structure
            # self.page.fill('input[type="email"]', os.environ.get("MS_USERNAME", config.USERNAME))
            # self.page.click("input[type='submit']")
            # self.page.fill('input[type="password"]', os.environ.get("MS_PASSWORD", config.PASSWORD))
            # self.page.click("input[type='submit']")
            
            # Wait for navigation to complete after login
            self.page.wait_for_load_state("networkidle")
            logger.info("Login completed")

    def open_notebook(self, notebook_name: str = None) -> None:
        """
        Open the specified notebook.
        
        Args:
            notebook_name: Name of the notebook to open. Defaults to config value.
            
        Raises:
            BrowserAutomationError: If the notebook cannot be found or opened.
        """
        notebook_name = notebook_name or config.NOTEBOOK_NAME
        
        try:
            logger.info(f"Opening notebook: {notebook_name}")
            
            # Wait for notebooks to load
            self.page.wait_for_selector(".NotebookListItem", timeout=self.timeout)
            
            # Click on the notebook with the specified name
            notebook_selector = f"//div[contains(@class, 'NotebookListItem') and contains(., '{notebook_name}')]"
            self.page.click(notebook_selector)
            
            # Wait for the notebook to open
            self.page.wait_for_load_state("networkidle")
            
            logger.info(f"Successfully opened notebook: {notebook_name}")
            
        except Exception as e:
            raise BrowserAutomationError(f"Failed to open notebook '{notebook_name}': {str(e)}")

    def create_or_open_section(self, section_name: str) -> None:
        """
        Create a new section or open an existing one.
        
        Args:
            section_name: Name of the section to create or open.
            
        Raises:
            BrowserAutomationError: If the section cannot be created or opened.
        """
        try:
            logger.info(f"Looking for section: {section_name}")
            
            # Check if section already exists
            section_selector = f"//div[contains(@class, 'SectionItem') and contains(., '{section_name}')]"
            section_exists = self.page.is_visible(section_selector, timeout=5000)
            
            if section_exists:
                logger.info(f"Section '{section_name}' already exists, opening it")
                self.page.click(section_selector)
            else:
                logger.info(f"Creating new section: {section_name}")
                
                # Click on the "Add section" button
                self.page.click("button[aria-label='Add section']")
                
                # Wait for the input field and enter section name
                self.page.wait_for_selector("input[placeholder='Name']")
                self.page.fill("input[placeholder='Name']", section_name)
                
                # Press Enter to create the section
                self.page.press("input[placeholder='Name']", "Enter")
                
                # Wait for the section to be created
                self.page.wait_for_selector(section_selector)
                
                logger.info(f"Successfully created section: {section_name}")
            
            # Wait for the section to load
            self.page.wait_for_load_state("networkidle")
            
        except Exception as e:
            raise BrowserAutomationError(f"Failed to create or open section '{section_name}': {str(e)}")

    def create_or_update_page(self, title: str, content: str) -> None:
        """
        Create a new page or update an existing one.
        
        Args:
            title: Title of the page.
            content: Content to add to the page.
            
        Raises:
            BrowserAutomationError: If the page cannot be created or updated.
        """
        try:
            logger.info(f"Creating or updating page: {title}")
            
            # Check if page already exists
            page_selector = f"//div[contains(@class, 'PageListItem') and contains(., '{title}')]"
            page_exists = self.page.is_visible(page_selector, timeout=5000)
            
            if page_exists:
                logger.info(f"Page '{title}' already exists, opening it")
                self.page.click(page_selector)
            else:
                logger.info(f"Creating new page: {title}")
                
                # Click on the "Add page" button
                self.page.click("button[aria-label='Add page']")
                
                # Wait for the editor to load
                self.page.wait_for_selector("div[contenteditable='true']")
                
                # Enter the title (first line becomes the title)
                self.page.fill("div[contenteditable='true']", title)
                self.page.press("div[contenteditable='true']", "Enter")
                
                logger.info(f"Successfully created page: {title}")
            
            # Add content to the page
            logger.info("Adding content to the page")
            
            # Wait for the editor to be ready
            self.page.wait_for_selector("div[contenteditable='true']")
            
            # Place cursor at the end of existing content
            self.page.click("div[contenteditable='true']")
            self.page.keyboard.press("End")
            self.page.keyboard.press("Enter")
            
            # Add the new content
            self.page.keyboard.type(content)
            
            # Give time for content to be saved
            time.sleep(2)
            
            logger.info("Successfully added content to the page")
            
        except Exception as e:
            raise BrowserAutomationError(f"Failed to create or update page '{title}': {str(e)}")

    def update_from_excel_data(self, data: Dict[str, Union[str, List[Dict[str, Any]]]]) -> None:
        """
        Update OneNote with formatted data from Excel.
        
        Args:
            data: Dictionary containing formatted Excel data.
            
        Raises:
            BrowserAutomationError: If the update process fails.
        """
        try:
            # Extract data
            date = data.get("date")
            title = data.get("title")
            records = data.get("records", [])
            
            # Create or open a section with the date
            self.create_or_open_section(date)
            
            # Prepare content
            content = f"# {title}\n\n"
            content += f"Updated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # Add table header if records exist
            if records and len(records) > 0:
                columns = list(records[0].keys())
                content += "## Data Summary\n\n"
                
                # Create a simple table with data
                content += "| " + " | ".join(columns) + " |\n"
                content += "| " + " | ".join(["---" for _ in columns]) + " |\n"
                
                # Add rows (limit to first 10 for readability)
                for record in records[:10]:
                    content += "| " + " | ".join([str(record.get(col, "")) for col in columns]) + " |\n"
                
                if len(records) > 10:
                    content += f"\n*Showing 10 of {len(records)} records*\n\n"
                
                # Add summary statistics
                content += "\n## Statistics\n\n"
                content += f"Total records: {len(records)}\n\n"
                
                # You could add more statistics here based on your data
            
            # Create or update the page
            self.create_or_update_page(title, content)
            
            logger.info(f"Successfully updated OneNote with data for {date}")
            
        except Exception as e:
            raise BrowserAutomationError(f"Failed to update OneNote with Excel data: {str(e)}")


if __name__ == "__main__":
    # Test the module
    with OneNoteUpdater() as updater:
        try:
            print("Browser started successfully")
            # Other test operations would go here
        except BrowserAutomationError as e:
            print(f"Error: {str(e)}")
