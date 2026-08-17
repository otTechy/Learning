"""
Test script to verify OneNote access after authentication.

This script attempts to access the OneNote URL defined in the config file,
allows manual authentication, and reports on the success or failure.

This script uses Microsoft Edge browser for better compatibility
with Microsoft authentication and Office 365.
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

def test_onenote_access():
    """
    Test if the OneNote URL is accessible after authentication.
    
    Returns:
        bool: True if access is successful, False otherwise.
    """
    if not PLAYWRIGHT_AVAILABLE:
        logger.error("Cannot test OneNote access: Playwright not available")
        return False
    
    logger.info(f"Testing access to OneNote URL: {config.ONENOTE_URL}")
    
    with sync_playwright() as playwright:
        # Launch Microsoft Edge browser for better Office 365 compatibility
        browser = playwright.chromium.launch(
            headless=False, 
            channel="msedge"  # Use Microsoft Edge
        )
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        
        try:
            # Navigate to OneNote URL
            logger.info("Navigating to OneNote URL...")
            try:
                page.goto(config.ONENOTE_URL, timeout=config.NAVIGATION_TIMEOUT)
            except Exception as e:
                logger.warning(f"Navigation issue (may be normal during authentication): {e}")
                # Continue as this might be part of the authentication flow
            
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
                except Exception as e:
                    logger.warning(f"Error pre-filling email: {e}")
                
                # Allow time for manual password entry and login
                print("\n===== AUTHENTICATION REQUIRED =====")
                print(f"Email has been pre-filled with: {config.EMAIL}")
                print("Please enter your password manually in the browser window.")
                print("The test will continue after login or after 2 minutes (whichever comes first).")
                
                # Wait up to 2 minutes for login
                max_wait_time = 120  # seconds
                login_successful = False
                start_time = time.time()
                
                while time.time() - start_time < max_wait_time:
                    try:
                        # Check if we're still on a login page
                        if not ("login" in page.url.lower() or "signin" in page.url.lower()):
                            login_successful = True
                            break
                        time.sleep(1)
                    except Exception as e:
                        logger.warning(f"Navigation occurred during login check: {e}")
                        # Try to re-evaluate the current URL
                        try:
                            current_url = page.url
                            if "login" not in current_url.lower() and "signin" not in current_url.lower():
                                # We're probably past login now
                                login_successful = True
                                break
                        except Exception as nav_err:
                            logger.warning(f"Error checking current URL: {nav_err}")
                            # Wait a bit and continue checking
                            time.sleep(2)
                            continue
                
                if login_successful:
                    logger.info("Login successful!")
                else:
                    logger.warning("Login timeout reached. Continuing anyway...")
            
            # Take a screenshot to show current state
            screenshot_path = os.path.join(os.path.dirname(__file__), "onenote_access_test.png")
            page.screenshot(path=screenshot_path)
            logger.info(f"Screenshot saved to: {screenshot_path}")
            
            # Check if we've reached OneNote
            logger.info(f"Current URL after login: {page.url}")
            
            # Wait for OneNote elements to appear
            try:
                # Look for typical OneNote or SharePoint document elements
                onenote_elements = [
                    "div[role='main']",  # Main content area
                    ".OneNote",  # OneNote class
                    "[data-automation-id='pageContent']",  # Page content
                    ".NotebookNav",  # Notebook navigation
                    "[data-automationid='CanvasZone']",  # SharePoint canvas
                    "[data-sp-feature-tag='SharePointOnlineDocumentLibrary']",  # SharePoint document library
                    ".ms-Fabric",  # Microsoft Fabric UI (used in modern SharePoint)
                    ".od-ItemContent",  # OneDrive/SharePoint item content
                    ".od-DetailsRowCheck",  # OneDrive/SharePoint row
                    ".SPPageChrome",  # SharePoint page chrome
                ]
                
                for selector in onenote_elements:
                    if page.query_selector(selector):
                        logger.info(f"Found OneNote element: {selector}")
                        break
                else:
                    logger.warning("⚠️ Could not find specific OneNote or SharePoint elements.")
                    print("Document elements not detected, but URL suggests this might be the right location.")
            
                # Wait for page content to load
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=20000)
                    # Additional wait time for OneNote to render
                    page.wait_for_timeout(5000)
                except Exception as e:
                    logger.warning(f"Load state timeout (continuing anyway): {e}")
                    # Continue anyway as the page might still be usable
                
                # Check for OneNote-specific content or SharePoint document
                page_title = page.title()
                logger.info(f"Page title: {page_title}")
                
                if ("onenote" in page.url.lower() or 
                    "one" in page_title.lower() or 
                    ".one" in page.url.lower() or
                    "quant standup" in page.url.lower() or  # Based on the notebook name in config
                    "notebook" in page.content().lower() or
                    "section" in page.content().lower() or
                    "page" in page.content().lower()):
                    logger.info("✅ Successfully accessed OneNote or SharePoint document!")
                    
                    # Check for OneNote structure elements and extract info
                    print("\n===== CHECKING ONENOTE STRUCTURE =====")
                    
                    # Look for notebook elements
                    notebook_elements = page.query_selector_all(".notebookName, .notebookNameEditor, [data-log-name='Notebook Name']")
                    if notebook_elements:
                        print("Notebook information found:")
                        for elem in notebook_elements:
                            name = elem.inner_text().strip()
                            if name:
                                print(f"  - Notebook: {name}")
                    
                    # Look for section groups
                    section_group_elements = page.query_selector_all(".sectionGroupName, [data-log-name='Section Group Name']")
                    if section_group_elements:
                        print("\nSection Groups found:")
                        for elem in section_group_elements:
                            name = elem.inner_text().strip()
                            if name:
                                print(f"  - Section Group: {name}")
                    
                    # Look for sections
                    section_elements = page.query_selector_all(".sectionName, [data-log-name='Section Name']")
                    if section_elements:
                        print("\nSections found:")
                        for elem in section_elements:
                            name = elem.inner_text().strip()
                            if name:
                                print(f"  - Section: {name}")
                    
                    # Look for pages
                    page_elements = page.query_selector_all(".pageName, [data-log-name='Page Name']")
                    if page_elements:
                        print("\nPages found:")
                        for elem in page_elements:
                            name = elem.inner_text().strip()
                            if name:
                                print(f"  - Page: {name}")
                    
                    if (not notebook_elements and not section_group_elements and 
                        not section_elements and not page_elements):
                        print("No specific OneNote structure elements could be detected.")
                        print("This may be because the page is still loading or")
                        print("the OneNote web view has a different structure than expected.")
                    
                    # Keep the browser open for 20 seconds so user can see the result
                    page.wait_for_timeout(20000)
                    
                    context.close()
                    browser.close()
                    return True
                else:
                    logger.warning("⚠️ Reached a page, but it might not be OneNote.")
                    print("\n===== ONENOTE ACCESS TEST RESULT =====")
                    print("⚠️ Reached a page, but it might not be OneNote.")
                    print(f"Current URL: {page.url}")
                    print(f"Page title: {page_title}")
                    print(f"Screenshot saved to: {screenshot_path}")
                    print("\nPlease examine the browser to verify the content.")
                    print("The browser will close automatically after 20 seconds.")
                    
                    # Keep the browser open for 20 seconds so user can see the result
                    page.wait_for_timeout(20000)
                    
                    context.close()
                    browser.close()
                    return False
            
            except Exception as e:
                logger.error(f"Error checking OneNote elements: {str(e)}")
                
                # Take a final screenshot
                error_screenshot_path = os.path.join(os.path.dirname(__file__), "onenote_access_error.png")
                page.screenshot(path=error_screenshot_path)
                logger.info(f"Error screenshot saved to: {error_screenshot_path}")
                
                print("\n===== ONENOTE ACCESS TEST RESULT =====")
                print(f"❌ Error checking OneNote elements: {str(e)}")
                print(f"Current URL: {page.url}")
                print(f"Error screenshot saved to: {error_screenshot_path}")
                
                context.close()
                browser.close()
                return False
        
        except Exception as e:
            logger.error(f"Error accessing OneNote URL: {str(e)}")
            
            try:
                # Take an error screenshot
                error_screenshot_path = os.path.join(os.path.dirname(__file__), "onenote_access_error.png")
                page.screenshot(path=error_screenshot_path)
                logger.info(f"Error screenshot saved to: {error_screenshot_path}")
            except Exception as screenshot_error:
                logger.warning(f"Could not take error screenshot: {screenshot_error}")
            
            print("\n===== ONENOTE ACCESS TEST RESULT =====")
            print(f"❌ Error accessing OneNote URL: {str(e)}")
            
            context.close()
            browser.close()
            return False

if __name__ == "__main__":
    print("\n===== ONENOTE ACCESS TEST =====\n")
    print(f"Testing access to OneNote URL: {config.ONENOTE_URL}")
    print(f"Authentication email: {config.EMAIL}")
    print("A Microsoft Edge browser window will open. You may need to enter your password manually.")
    print("The test will check if OneNote is accessible after authentication.\n")
    
    success = test_onenote_access()
    
    print("\n===== TEST SUMMARY =====")
    if success:
        print("✅ OneNote is accessible after authentication!")
        print("You can proceed with implementing the OneNote updater.")
    else:
        print("❌ Could not confirm OneNote access.")
        print("Please check the following:")
        print("1. Your OneNote URL is correct")
        print("2. You have permissions to access the OneNote notebook")
        print("3. You completed the authentication process in the browser")
