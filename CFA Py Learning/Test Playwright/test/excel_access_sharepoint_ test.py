"""
Test script to verify Excel file access after authentication.

This script attempts to access the Excel file URL defined in the config file,
uses Microsoft Edge to leverage better compatibility with SharePoint,
and reports on the success or failure.
"""

import sys
import os
import logging
import time
import tempfile
import subprocess
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

def get_chrome_user_data_dir():
    """
    Try to find the Chrome user data directory for the current user.
    This helps access the existing Chrome profile with cookies and logins.
    
    Returns:
        str: Path to Chrome user data directory, or None if not found
    """
    user_home = os.path.expanduser("~")
    
    # Common paths for Chrome user data by OS
    paths = {
        'win32': [
            os.path.join(user_home, 'AppData', 'Local', 'Google', 'Chrome', 'User Data'),
            os.path.join(user_home, 'Local Settings', 'Application Data', 'Google', 'Chrome', 'User Data'),
        ],
        'darwin': [
            os.path.join(user_home, 'Library', 'Application Support', 'Google', 'Chrome'),
        ],
        'linux': [
            os.path.join(user_home, '.config', 'google-chrome'),
            os.path.join(user_home, '.config', 'chromium'),
        ]
    }
    
    # Get paths for current OS
    os_paths = paths.get(sys.platform, [])
    
    # Check which paths exist
    for path in os_paths:
        if os.path.exists(path):
            logger.info(f"Found Chrome user data directory: {path}")
            return path
    
    logger.warning("Could not find Chrome user data directory")
    return None

def get_running_chrome_debugging_port():
    """
    Check if Chrome is already running with remote debugging enabled.
    This function is no longer used since we're using Edge.
    
    Returns:
        int: The debugging port if available, None otherwise
    """
    try:
        # For Windows
        if sys.platform == 'win32':
            cmd = 'tasklist /FI "IMAGENAME eq chrome.exe" /V /FO CSV'
            output = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
            
            # Look for debugging port in command line
            debugging_lines = [line for line in output.splitlines() if '--remote-debugging-port=' in line]
            if debugging_lines:
                for line in debugging_lines:
                    port_index = line.find('--remote-debugging-port=')
                    if port_index > 0:
                        port_str = line[port_index + 23:].split(' ')[0].split(',')[0]
                        try:
                            return int(port_str)
                        except ValueError:
                            pass
        
        return None
    except Exception as e:
        logger.error(f"Error checking for running Chrome instance: {e}")
        return None

def test_excel_access():
    """
    Test if the Excel file URL is accessible after authentication.
    Uses Microsoft Edge for better compatibility with SharePoint.
    
    Returns:
        bool: True if access is successful, False otherwise.
    """
    if not PLAYWRIGHT_AVAILABLE:
        logger.error("Cannot test Excel access: Playwright not available")
        return False
    
    logger.info(f"Testing access to Excel file URL: {config.EXCEL_FILE_PATH}")
    
    # Create temporary directory for downloads
    temp_download_dir = tempfile.mkdtemp()
    logger.info(f"Created temporary download directory: {temp_download_dir}")
    
    with sync_playwright() as playwright:
        browser = None
        
        try:
            # Launch Microsoft Edge browser
            logger.info("Launching Microsoft Edge browser...")
            browser = playwright.chromium.launch(
                headless=False,
                channel="msedge",  # Use Microsoft Edge
            )
            
            # Create a new context (only if we launched a new browser)
            if hasattr(browser, "new_context"):
                context = browser.new_context(
                    accept_downloads=True,
                    viewport={"width": 1280, "height": 800},
                )
                page = context.new_page()
            else:
                # When connecting to existing browser, we need to use the default context
                default_context = browser.contexts[0] if browser.contexts else browser.new_context()
                page = default_context.new_page()
            
            # Navigate to Excel URL
            logger.info("Navigating to Excel URL...")
            page.goto(config.EXCEL_FILE_PATH, timeout=config.NAVIGATION_TIMEOUT)
            
            # Take a screenshot of initial state
            initial_screenshot_path = os.path.join(os.path.dirname(__file__), "excel_access_initial.png")
            page.screenshot(path=initial_screenshot_path)
            logger.info(f"Initial screenshot saved to: {initial_screenshot_path}")
            
            # Check if we're redirected to a login page
            if "login" in page.url.lower() or "signin" in page.url.lower():
                logger.info("Redirected to login page. Helping with authentication...")
                
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
                    
                    # Allow time for manual password entry
                    print("\n===== MANUAL PASSWORD ENTRY REQUIRED =====")
                    print(f"Email has been pre-filled with: {config.EMAIL}")
                    print("Please enter your password manually in the browser window.")
                    print("The test will continue after login or after 2 minutes (whichever comes first).")
                
                except Exception as e:
                    logger.warning(f"Could not pre-fill email: {e}")
                    print("\n===== MANUAL AUTHENTICATION REQUIRED =====")
                    print("Please log in with your Microsoft account in the browser window.")
                    print("The test will continue after login or after 2 minutes (whichever comes first).")
                
                # Wait up to 2 minutes for login
                max_wait_time = 120  # seconds
                login_successful = False
                
                for _ in range(max_wait_time):
                    # Check if we're still on a login page
                    if not ("login" in page.url.lower() or "signin" in page.url.lower()):
                        login_successful = True
                        break
                    time.sleep(1)
                
                if login_successful:
                    logger.info("Login successful!")
                else:
                    logger.warning("Login timeout reached. Continuing anyway...")
            
            # Wait for Excel Online elements to appear
            logger.info("Waiting for Excel Online elements...")
            page.wait_for_load_state("networkidle")
            
            # Take a screenshot after login/loading
            screenshot_path = os.path.join(os.path.dirname(__file__), "excel_access_test.png")
            page.screenshot(path=screenshot_path)
            logger.info(f"Screenshot saved to: {screenshot_path}")
            
            # Check if we've reached Excel or if the page is blank
            logger.info(f"Current URL after login: {page.url}")
            
            # Check for blank page scenario
            page_content = page.content()
            if page_content.strip() == "" or page_content.count("<") < 10:
                logger.warning("Page appears to be blank or has minimal content")
                print("\n===== BLANK PAGE DETECTED =====")
                print("The page appears to be blank after authentication.")
                print("This can happen with SharePoint links to Office documents.")
                print("\nTry these alternative approaches:")
                print("1. Open Excel Desktop app and sign in with your Microsoft account")
                print("2. Go to https://www.office.com/ and navigate to your files")
                print("3. Try different Excel access options:")
                
                # Offer different options to handle the blank page
                print("\nWould you like to:")
                print("1. Try to open in Desktop Excel app (if available)")
                print("2. Try to open in Office.com")
                print("3. Retry the current page")
                print("4. Skip and continue")
                
                choice = input("Enter your choice (1-4): ")
                
                if choice == "1":
                    # Try to trigger "Open in Desktop App"
                    logger.info("Trying to open in Desktop Excel app...")
                    desktop_app_selectors = [
                        "button:has-text('Open in Desktop App')",
                        "a:has-text('Open in Desktop App')",
                        "[aria-label='Open in Excel']",
                        "[title='Open in Excel']",
                    ]
                    
                    for selector in desktop_app_selectors:
                        app_button = page.query_selector(selector)
                        if app_button:
                            logger.info(f"Found desktop app button: {selector}")
                            app_button.click()
                            print("Attempted to open in Desktop Excel. Please check if Excel is opening.")
                            page.wait_for_timeout(10000)  # Wait 10 seconds
                            break
                    else:
                        # If no button found, try navigating to the Excel URL with different parameters
                        excel_url = config.EXCEL_FILE_PATH
                        # Add parameter to try to trigger desktop app
                        if "?" in excel_url:
                            excel_url += "&web=0"
                        else:
                            excel_url += "?web=0"
                            
                        logger.info(f"Navigating to URL with desktop app parameter: {excel_url}")
                        page.goto(excel_url)
                        page.wait_for_timeout(10000)  # Wait 10 seconds
                
                elif choice == "2":
                    # Try to open in Office.com
                    logger.info("Navigating to Office.com...")
                    page.goto("https://www.office.com/")
                    page.wait_for_load_state("networkidle")
                    
                    # Look for Excel or Documents links
                    office_selectors = [
                        "a:has-text('Excel')",
                        "a:has-text('Documents')",
                        "[aria-label='Excel']",
                        "[aria-label='Documents']",
                    ]
                    
                    for selector in office_selectors:
                        office_link = page.query_selector(selector)
                        if office_link:
                            logger.info(f"Found Office.com link: {selector}")
                            office_link.click()
                            print("Navigated to Office.com. Please manually locate your Excel file.")
                            page.wait_for_timeout(60000)  # Wait 60 seconds for manual navigation
                            break
                    else:
                        print("Could not find Excel or Documents links on Office.com")
                        print("Please manually navigate to your files.")
                        page.wait_for_timeout(60000)  # Wait 60 seconds for manual navigation
                
                elif choice == "3":
                    # Retry current page
                    logger.info("Retrying current page...")
                    page.reload()
                    page.wait_for_load_state("networkidle")
                    page.wait_for_timeout(5000)  # Wait 5 seconds after reload
                
                # For choice 4 or any other input, just continue
                
                # Take a new screenshot after the chosen action
                post_action_screenshot = os.path.join(os.path.dirname(__file__), "excel_post_action.png")
                page.screenshot(path=post_action_screenshot)
                logger.info(f"Post-action screenshot saved to: {post_action_screenshot}")
            
            # Look for Excel-specific elements
            excel_elements = [
                ".ExcelCanvas",  # Excel canvas
                "[data-automation-id='CanvasSection']",  # Canvas section
                ".SpreadsheetMenuBar",  # Spreadsheet menu bar
                "#WebApplicationFrame",  # Web application frame
                "iframe#WebApplicationFrame",  # Excel iframe
                "div.BreadcrumbTitle",  # Breadcrumb title that might contain file name
                "[data-automation-id='commandBarWrapper']",  # Command bar in Excel Online
                ".ms-CommandBar",  # Command bar
                ".ewa-filemenu",  # Excel Web App file menu
                "div[role='grid']",  # Excel grid
            ]
            
            excel_found = False
            for selector in excel_elements:
                if page.query_selector(selector):
                    logger.info(f"Found Excel element: {selector}")
                    excel_found = True
                    break
            
            # If no specific elements found, check URL and title
            if not excel_found:
                page_title = page.title()
                logger.info(f"Page title: {page_title}")
                
                # Check if the title contains Excel file extension or name
                if (
                    "excel" in page.url.lower() or 
                    "excel" in page_title.lower() or
                    ".xls" in page_title.lower() or
                    "spreadsheet" in page_title.lower() or
                    "jira_tracker" in page_title.lower() or
                    "jira tracker" in page_title.lower()
                ):
                    logger.info("URL or title suggests Excel content")
                    excel_found = True
                
                # If user confirms they can see Excel content, consider it found
                if not excel_found:
                    print("\nThe test couldn't automatically detect Excel elements.")
                    print("Can you see the Excel spreadsheet content in the browser? (y/n)")
                    user_confirms = input("> ")
                    if user_confirms.lower() == "y":
                        logger.info("User confirms Excel content is visible")
                        excel_found = True
            
            # Look for download options
            download_elements = [
                "button:has-text('Download')",
                "button:has-text('Open in Desktop App')",
                "[aria-label='Download']",
                "[title='Download']",
            ]
            
            for selector in download_elements:
                download_button = page.query_selector(selector)
                if download_button:
                    logger.info(f"Found download element: {selector}")
                    print("\nFound a download button. Would you like to:")
                    print("1. Click the download button")
                    print("2. Continue without downloading")
                    choice = input("Enter your choice (1 or 2): ")
                    
                    if choice == "1":
                        logger.info("Clicking download button...")
                        download_button.click()
                        
                        # Wait for download dialog or actual download
                        print("Waiting for download to start or dialog to appear...")
                        page.wait_for_timeout(5000)
                        
                        # Check for download dialog
                        dialog_elements = [
                            "button:has-text('Save')",
                            "button:has-text('Open')",
                            "button:has-text('Save As')",
                        ]
                        
                        for dialog_selector in dialog_elements:
                            dialog_button = page.query_selector(dialog_selector)
                            if dialog_button:
                                logger.info(f"Found dialog button: {dialog_selector}")
                                print("Please handle the download dialog manually.")
                                page.wait_for_timeout(10000)  # Give time to handle dialog
                                break
                    
                    break
            
            # Final result
            if excel_found:
                logger.info("✅ Successfully accessed Excel file!")
                
                # Look for download options
                print("\n===== DOWNLOAD OPTIONS =====")
                print("Looking for download options...")
                
                download_elements = [
                    "button:has-text('Download')",
                    "button:has-text('Open in Desktop App')",
                    "[aria-label='Download']",
                    "[title='Download']",
                    "[data-automationid='DownloadButton']",
                    "[data-is-focusable='true']:has-text('Download')",
                ]
                
                for selector in download_elements:
                    download_button = page.query_selector(selector)
                    if download_button:
                        logger.info(f"Found download element: {selector}")
                        print(f"Found download button: {selector}")
                        print("Would you like to automatically click it? (y/n)")
                        choice = input("> ")
                        
                        if choice.lower() == "y":
                            logger.info("Clicking download button...")
                            try:
                                download_button.click()
                                print("Download button clicked. Please handle any dialogs that appear.")
                                page.wait_for_timeout(5000)
                            except Exception as e:
                                logger.error(f"Error clicking download button: {e}")
                        break
                else:
                    print("No specific download button found.")
                    print("You may need to manually download the file.")
                
                # Give user time to see the result
                print("\n===== EXCEL ACCESS TEST RESULT =====")
                print("✅ Successfully accessed Excel file!")
                print(f"Current page title: {page.title()}")
                print(f"Screenshot saved to: {screenshot_path}")
                print("\nPlease examine the browser to verify Excel content is visible.")
                print("The browser will close automatically after 20 seconds.")
                
                # Keep the browser open for 20 seconds so user can see the result
                page.wait_for_timeout(20000)
                
                # Close browser if we created it
                if hasattr(browser, "close"):
                    browser.close()
                return True
            else:
                logger.warning("⚠️ Could not confirm Excel access.")
                print("\n===== EXCEL ACCESS TEST RESULT =====")
                print("⚠️ Could not confirm Excel access.")
                print(f"Current URL: {page.url}")
                print(f"Page title: {page.title()}")
                print(f"Screenshot saved to: {screenshot_path}")
                print("\nPlease examine the browser to verify the content.")
                print("The browser will close automatically after 20 seconds.")
                
                # Keep the browser open for 20 seconds so user can see the result
                page.wait_for_timeout(20000)
                
                # Close browser if we created it
                if hasattr(browser, "close"):
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
            
            print("\n===== EXCEL ACCESS TEST RESULT =====")
            print(f"❌ Error accessing Excel URL: {str(e)}")
            
            # Close browser if we created it and it's still open
            if browser and hasattr(browser, "close"):
                browser.close()
            return False

if __name__ == "__main__":
    print("\n===== EXCEL ACCESS TEST =====\n")
    print(f"Testing access to Excel URL: {config.EXCEL_FILE_PATH}")
    print("A Microsoft Edge browser window will open. You may need to log in manually.")
    print("Edge often works better with SharePoint and Office 365 content.")
    print("The test will check if the Excel file is accessible after authentication.\n")
    
    success = test_excel_access()
    
    print("\n===== TEST SUMMARY =====")
    if success:
        print("✅ Excel file is accessible after authentication!")
        print("The test has confirmed you can access the Excel file.")
        print("You can proceed with implementing the Excel reader.")
    else:
        print("❌ Test could not automatically confirm Excel file access.")
        print("However, if you could see the Excel content in the browser, the file is accessible.")
        print("You may proceed with implementing the Excel reader if you confirmed visual access.")
        print("\nCheck the following if you had issues:")
        print("1. Your Excel file URL is correct")
        print("2. You have permissions to access the Excel file")
        print("3. You completed the authentication process in the browser")
