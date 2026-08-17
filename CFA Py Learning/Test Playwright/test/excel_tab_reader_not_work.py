"""
Excel tab reader test script.

This script uses browser automation to access a SharePoint Excel file,
extract data from a specific tab, and display the contents without downloading.
"""

import sys
import os
import logging
import time
from pathlib import Path

# Add parent directory to path so we can import modules
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    logger.error("Playwright not installed. Please install with: pip install playwright")
    logger.error("Then install browsers with: python -m playwright install")
    PLAYWRIGHT_AVAILABLE = False

def extract_table_data_from_browser(page):
    """
    Extract table data directly from the browser.
    
    Args:
        page: Playwright page object with loaded Excel content
        
    Returns:
        dict: Extracted table data or None if extraction failed
    """
    try:
        print("\n===== EXTRACTING TABLE DATA FROM BROWSER =====")
        
        # Take a screenshot to see what we're working with
        screenshot_path = os.path.join(os.path.dirname(__file__), "excel_view.png")
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")
        
        # Extract visible data from the Excel web view
        # First, check if we're in the correct tab/sheet
        print(f"Looking for data in tab: {config.SHEET_NAME}")
        
        # Look for tab indicators or sheet name in the page
        sheet_tabs = page.query_selector_all('[role="tab"]')
        current_tab_name = None
        
        for tab in sheet_tabs:
            tab_text = tab.inner_text().strip()
            print(f"Found sheet tab: {tab_text}")
            if tab_text == config.SHEET_NAME:
                current_tab_name = tab_text
                if not tab.get_attribute("aria-selected") == "true":
                    print(f"Clicking on tab: {tab_text}")
                    tab.click()
                    page.wait_for_timeout(2000)  # Wait for sheet to load
                break
        
        if current_tab_name:
            print(f"Current tab: {current_tab_name}")
        else:
            print(f"Could not confirm we're on tab '{config.SHEET_NAME}'. Using visible data.")
        
        # Extract table data from the Excel web view
        # Look for grid/table elements in the page
        table_data = []
        
        # Try different selectors for Excel Online table elements
        grid_selectors = [
            "div[role='grid']",
            "div.excel-table",
            "div.ms-DetailsList",
            ".office-excel-canvas",
            "div[data-automationid='GridCanvas']"
        ]
        
        grid_element = None
        for selector in grid_selectors:
            grid_element = page.query_selector(selector)
            if grid_element:
                print(f"Found grid element with selector: {selector}")
                break
        
        if grid_element:
            # Try to extract header row
            header_rows = page.query_selector_all("div[role='row'][aria-rowindex='1'], .ms-DetailsList-headerRow")
            headers = []
            
            if header_rows and len(header_rows) > 0:
                header_cells = header_rows[0].query_selector_all("div[role='columnheader']")
                for cell in header_cells:
                    headers.append(cell.inner_text().strip())
            
            # Extract data rows
            data_rows = page.query_selector_all("div[role='row'][aria-rowindex]")
            
            print(f"Found {len(data_rows)} data rows")
            
            # Process first 10 rows maximum
            max_rows = min(10, len(data_rows))
            
            # If we couldn't get headers, assume generic column names
            if not headers:
                # Count cells in first row to determine number of columns
                if data_rows and len(data_rows) > 0:
                    first_row_cells = data_rows[0].query_selector_all("div[role='gridcell']")
                    headers = [f"Column {i+1}" for i in range(len(first_row_cells))]
                else:
                    headers = ["Column 1"]  # Fallback
            
            # Extract row data
            print(f"Headers: {headers}")
            print("\n===== TABLE DATA PREVIEW =====")
            
            for i in range(min(5, max_rows)):  # Show preview of first 5 rows
                row = data_rows[i]
                cells = row.query_selector_all("div[role='gridcell']")
                
                row_data = {}
                for j, cell in enumerate(cells):
                    if j < len(headers):
                        header = headers[j]
                        value = cell.inner_text().strip()
                        row_data[header] = value
                
                table_data.append(row_data)
                print(f"Row {i+1}: {row_data}")
            
            return {
                "sheet_name": current_tab_name or config.SHEET_NAME,
                "headers": headers,
                "rows": table_data,
                "total_rows_found": len(data_rows)
            }
        else:
            print("Could not find grid/table element in the page")
            
            # As a fallback, try to get any structured data from the page
            print("Attempting to extract any visible table data...")
            
            # This is a fallback approach that attempts to extract any tabular data
            table_elements = page.query_selector_all("table")
            if table_elements and len(table_elements) > 0:
                print(f"Found {len(table_elements)} table elements")
                
                # Extract from the first table
                fallback_table = table_elements[0]
                header_cells = fallback_table.query_selector_all("th")
                fallback_headers = [cell.inner_text().strip() for cell in header_cells]
                
                fallback_rows = []
                row_elements = fallback_table.query_selector_all("tr")
                
                for row_elem in row_elements[:5]:  # First 5 rows only
                    cell_elements = row_elem.query_selector_all("td")
                    if cell_elements:
                        row_data = {}
                        for i, cell in enumerate(cell_elements):
                            header = fallback_headers[i] if i < len(fallback_headers) else f"Column {i+1}"
                            row_data[header] = cell.inner_text().strip()
                        fallback_rows.append(row_data)
                
                return {
                    "sheet_name": config.SHEET_NAME,
                    "headers": fallback_headers,
                    "rows": fallback_rows,
                    "total_rows_found": len(row_elements)
                }
            
            print("No table data could be extracted from the page")
            return None
    
    except Exception as e:
        print(f"Error extracting table data: {e}")
        return None

def access_excel_tab():
    """
    Access the Excel tab specified in the config and extract its data
    without downloading the file.
    
    Returns:
        bool: True if access is successful, False otherwise.
    """
    if not PLAYWRIGHT_AVAILABLE:
        logger.error("Cannot access Excel tab: Playwright not available")
        return False
    
    logger.info(f"Accessing Excel file URL: {config.EXCEL_FILE_PATH}")
    logger.info(f"Target sheet: {config.SHEET_NAME}")
    
    with sync_playwright() as playwright:
        try:
            # Launch Microsoft Edge browser for better Office 365 compatibility
            logger.info("Launching Microsoft Edge browser...")
            browser = playwright.chromium.launch(
                headless=False,
                channel="msedge",  # Use Microsoft Edge
            )
            
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
            )
            
            page = context.new_page()
            
            # Navigate to Excel URL
            logger.info("Navigating to Excel URL...")
            try:
                page.goto(config.EXCEL_FILE_PATH, timeout=config.NAVIGATION_TIMEOUT)
            except Exception as e:
                logger.warning(f"Navigation issue (may be normal during authentication): {e}")
                # Continue as this might be part of the authentication flow
            
            # Check if we're redirected to a login page
            if "login" in page.url.lower() or "signin" in page.url.lower():
                logger.info("Redirected to login page. Helping with authentication...")
                print("\n===== AUTHENTICATION REQUIRED =====")
                print(f"Using email from config: {config.EMAIL}")
                
                # Pre-fill email if possible
                try:
                    # Look for email input field
                    email_input_selectors = [
                        "input[type='email']",
                        "input[name='loginfmt']",
                        "input[placeholder='Email, phone, or Skype']",
                    ]
                    
                    for selector in email_input_selectors:
                        email_input = page.query_selector(selector)
                        if email_input:
                            logger.info(f"Found email input field: {selector}")
                            # Fill the email
                            email_input.fill(config.EMAIL)
                            logger.info(f"Pre-filled email: {config.EMAIL}")
                            
                            # Look for next or submit button
                            next_button_selectors = [
                                "input[type='submit']",
                                "button[type='submit']",
                                "button:has-text('Next')",
                                "[aria-label='Next']",
                            ]
                            
                            for btn_selector in next_button_selectors:
                                next_button = page.query_selector(btn_selector)
                                if next_button:
                                    logger.info(f"Found next button: {btn_selector}")
                                    next_button.click()
                                    logger.info("Clicked next button")
                                    break
                            
                            break
                except Exception as e:
                    logger.error(f"Error pre-filling email: {e}")
                
                # Wait for manual authentication to complete
                print("\nPlease complete the authentication process in the browser.")
                print("Waiting for Excel content to appear (max 2 minutes)...")
                
                authentication_timeout = 120  # 2 minutes
                start_time = time.time()
                excel_detected = False
                
                while time.time() - start_time < authentication_timeout:
                    try:
                        # Check for indicators that we're on an Excel page
                        if ("Excel" in page.title() or 
                            "xls" in page.url.lower() or 
                            config.SHEET_NAME in page.content() or 
                            "Jira_Tracker" in page.title()):
                            excel_detected = True
                            break
                        
                        # Wait a bit before checking again
                        page.wait_for_timeout(2000)  # 2 seconds
                    except Exception as e:
                        logger.warning(f"Navigation occurred during authentication check: {e}")
                        # Try to re-navigate if we lost the page
                        try:
                            current_url = page.url
                            if "login" not in current_url.lower() and "signin" not in current_url.lower():
                                # We're probably past login now
                                excel_detected = True
                                break
                        except Exception as nav_err:
                            logger.warning(f"Error checking current URL: {nav_err}")
                            # Wait a bit and continue checking
                            time.sleep(2)
                            continue
                
                if not excel_detected:
                    logger.warning("Excel content not detected after authentication.")
                    print("\n❌ Excel content not detected after authentication.")
                    print("Please try again or check if the URL is correct.")
                    browser.close()
                    return False
                
                print("\n✅ Authentication successful!")
            
            # Wait for Excel to load
            logger.info("Waiting for Excel content to load...")
            print("Waiting for Excel content to load...")
            try:
                # Use a shorter timeout for the load state to avoid hanging
                page.wait_for_load_state("domcontentloaded", timeout=20000)  # 20 seconds
                # Additional wait time for Excel rendering
                page.wait_for_timeout(5000)
            except Exception as e:
                logger.warning(f"Load state timeout (continuing anyway): {e}")
                # Continue anyway as the page might still be usable
            
            # Take a screenshot to confirm what we're looking at
            screenshot_path = os.path.join(os.path.dirname(__file__), "excel_before_extract.png")
            page.screenshot(path=screenshot_path)
            logger.info(f"Screenshot saved to: {screenshot_path}")
            
            # Verify we have access to the Excel content
            logger.info("Verifying Excel content access...")
            if ("Excel" in page.title() or 
                "xls" in page.url.lower() or 
                config.SHEET_NAME in page.content() or
                "Jira_Tracker" in page.title()):
                logger.info("Excel content is accessible!")
                print("\n✅ Excel content is accessible!")
                
                # Extract data from the browser
                table_data = extract_table_data_from_browser(page)
                
                if table_data:
                    print("\n===== EXTRACTED EXCEL DATA SUMMARY =====")
                    print(f"Sheet name: {table_data['sheet_name']}")
                    print(f"Headers: {', '.join(table_data['headers'])}")
                    print(f"Total rows found: {table_data['total_rows_found']}")
                    print(f"Data preview: {len(table_data['rows'])} rows")
                    
                    # Display formatted data
                    print("\n===== DATA PREVIEW (FIRST 5 ROWS) =====")
                    for i, row in enumerate(table_data['rows']):
                        print(f"\nRow {i+1}:")
                        for header, value in row.items():
                            print(f"  {header}: {value}")
                else:
                    logger.warning("Could not extract table data from the Excel web view.")
                    print("\n⚠️ Could not extract table data from the Excel web view.")
                    print("This could be due to the way Excel renders in the browser.")
                    
                    # Fallback - take a screenshot of the visible content
                    print("\nSaving screenshot of visible Excel content...")
                    screenshot_path = os.path.join(os.path.dirname(__file__), "excel_content.png")
                    page.screenshot(path=screenshot_path)
                    print(f"Screenshot saved to: {screenshot_path}")
                    
                    # Ask the user to manually describe what they see
                    print("\nSince we couldn't automatically extract the data,")
                    print("please look at the Excel content in the browser and describe it briefly.")
                    print("What columns do you see in the sheet? (Press Enter when ready)")
                    input("> ")
                    
                    print("\nHow many rows of data are visible? (Just a rough estimate)")
                    input("> ")
                    
                    print("\nCould you describe the first few rows of data you see?")
                    input("> ")
                
                # Keep the browser open briefly
                print("\nKeeping browser open for 10 seconds to examine the Excel content...")
                page.wait_for_timeout(10000)
                
                browser.close()
                return True
            else:
                logger.warning("Could not verify Excel content access.")
                print("\n❌ Could not verify Excel content access.")
                browser.close()
                return False
            
        except Exception as e:
            logger.error(f"Error accessing Excel URL: {str(e)}")
            
            try:
                # Take an error screenshot
                error_screenshot_path = os.path.join(os.path.dirname(__file__), "excel_access_error.png")
                page.screenshot(path=error_screenshot_path)
                logger.info(f"Error screenshot saved to: {error_screenshot_path}")
            except Exception as screenshot_error:
                logger.warning(f"Could not take error screenshot: {screenshot_error}")
            
            print(f"\n❌ Error accessing Excel URL: {str(e)}")
            
            if browser:
                browser.close()
            return False

if __name__ == "__main__":
    print("\n===== EXCEL TAB READER TEST =====\n")
    print(f"Testing access to Excel tab: {config.SHEET_NAME}")
    print(f"Excel URL: {config.EXCEL_FILE_PATH}")
    print(f"Authentication email: {config.EMAIL}")
    print("\nA Microsoft Edge browser window will open. You may need to log in manually.")
    print("The test will extract data from the tab specified in your config file.\n")
    
    success = access_excel_tab()
    
    print("\n===== TEST SUMMARY =====")
    if success:
        print("✅ Excel tab data accessed successfully!")
        print(f"You can now view the extracted data from tab: {config.SHEET_NAME}")
    else:
        print("❌ Could not access Excel tab data.")
        print("Please check the following:")
        print("1. Your Excel file URL is correct")
        print("2. The sheet name in config is correct")
        print("3. You have permissions to access the Excel file")
        print("4. You completed the authentication process in the browser")
