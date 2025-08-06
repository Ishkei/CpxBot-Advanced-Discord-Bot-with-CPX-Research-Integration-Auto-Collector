#!/usr/bin/env python3
"""
Test Firefox Automation

This script tests the Firefox automation functionality.
"""

import time
from loguru import logger
from src.web_automation.firefox_automation import FirefoxAutomation
from selenium.webdriver.common.by import By


def test_basic_automation():
    """
    Test basic Firefox automation functionality.
    """
    logger.info("Testing Firefox automation...")
    
    with FirefoxAutomation(headless=False) as browser:
        # Test navigation
        test_url = "https://www.google.com"
        
        if browser.navigate_to_url(test_url):
            logger.info("✓ Successfully navigated to Google")
            logger.info(f"Page title: {browser.get_page_title()}")
            
            # Test taking screenshot
            if browser.take_screenshot("test_screenshot.png"):
                logger.info("✓ Screenshot taken successfully")
            
            # Test finding elements
            search_box = browser.find_element_safe(By.NAME, "q")
            if search_box:
                logger.info("✓ Found search box")
                
                # Test filling input
                if browser.fill_input(By.NAME, "q", "Firefox automation test"):
                    logger.info("✓ Successfully filled search box")
                
                # Wait a moment to see the result
                time.sleep(2)
                
                # Test clicking (submit search)
                if browser.click_element(By.NAME, "btnK"):
                    logger.info("✓ Successfully clicked search button")
                    time.sleep(3)
                else:
                    logger.info("Search button not found or not clickable")
            else:
                logger.warning("Search box not found")
        else:
            logger.error("✗ Failed to navigate to Google")
    
    logger.info("Firefox automation test completed!")


def test_survey_automation():
    """
    Test survey automation with a simple form.
    """
    logger.info("Testing survey automation...")
    
    with FirefoxAutomation(headless=False) as browser:
        # Navigate to a test form (using a simple HTML form)
        test_form_url = "https://httpbin.org/forms/post"
        
        if browser.navigate_to_url(test_form_url):
            logger.info("✓ Successfully navigated to test form")
            
            # Test filling form fields
            if browser.fill_input(By.NAME, "custname", "John Doe"):
                logger.info("✓ Filled customer name")
            
            if browser.fill_input(By.NAME, "custtel", "555-1234"):
                logger.info("✓ Filled phone number")
            
            if browser.fill_input(By.NAME, "custemail", "john@example.com"):
                logger.info("✓ Filled email")
            
            # Test dropdown selection
            if browser.select_option(By.NAME, "size", "large"):
                logger.info("✓ Selected size option")
            
            # Test checkbox
            if browser.click_element(By.NAME, "topping"):
                logger.info("✓ Selected topping")
            
            # Wait to see the form
            time.sleep(3)
            
            # Take screenshot
            browser.take_screenshot("form_test.png")
            
        else:
            logger.error("✗ Failed to navigate to test form")
    
    logger.info("Survey automation test completed!")


def main():
    """
    Run all tests.
    """
    print("Firefox Automation Tests")
    print("=" * 25)
    
    try:
        test_basic_automation()
        print("\n" + "=" * 25)
        test_survey_automation()
        print("\nAll tests completed!")
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        print(f"\nTest failed: {e}")


if __name__ == "__main__":
    main() 