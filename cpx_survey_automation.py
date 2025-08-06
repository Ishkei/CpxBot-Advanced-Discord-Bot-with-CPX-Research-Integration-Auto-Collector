#!/usr/bin/env python3
"""
CPX Research Survey Automation

This script provides specialized automation for CPX Research surveys.
"""

import time
import random
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger
from src.web_automation.firefox_automation import FirefoxAutomation


class CPXSurveyAutomation:
    """
    Specialized automation for CPX Research surveys.
    """
    
    def __init__(self, headless: bool = False):
        """
        Initialize CPX survey automation.
        
        Args:
            headless: Whether to run in headless mode
        """
        self.browser = FirefoxAutomation(headless=headless)
        self.cpx_url = "https://offers.cpx-research.com/index.php"
        self.user_id = "533055960609193994"
        self.app_id = "27260"
        
    def start_browser(self) -> bool:
        """Start the Firefox browser."""
        return self.browser.start_browser()
    
    def close_browser(self):
        """Close the Firefox browser."""
        self.browser.close_browser()
    
    def navigate_to_cpx(self) -> bool:
        """
        Navigate to CPX Research survey page.
        
        Returns:
            bool: True if navigation successful
        """
        url = f"{self.cpx_url}?app_id={self.app_id}&ext_user_id={self.user_id}"
        logger.info(f"Navigating to CPX Research: {url}")
        return self.browser.navigate_to_url(url)
    
    def wait_for_survey_questions(self, timeout: int = 30) -> bool:
        """
        Wait for survey questions to load.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            bool: True if questions found
        """
        try:
            # Wait for common survey question elements
            selectors = [
                "input[type='radio']",
                "input[type='checkbox']",
                "select",
                "textarea",
                "input[type='text']",
                ".question",
                "[class*='question']",
                "[id*='question']"
            ]
            
            for selector in selectors:
                try:
                    WebDriverWait(self.browser.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Found survey questions with selector: {selector}")
                    return True
                except:
                    continue
            
            logger.warning("No survey questions found")
            return False
            
        except Exception as e:
            logger.error(f"Error waiting for survey questions: {e}")
            return False
    
    def answer_radio_question(self, question_text: str = None, answer_index: int = 0) -> bool:
        """
        Answer a radio button question.
        
        Args:
            question_text: Text to search for in question (optional)
            answer_index: Index of answer to select (0-based)
            
        Returns:
            bool: True if successful
        """
        try:
            # Find all radio buttons on the page
            radio_buttons = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            
            if not radio_buttons:
                logger.warning("No radio buttons found")
                return False
            
            # Group radio buttons by name (question)
            radio_groups = {}
            for radio in radio_buttons:
                name = radio.get_attribute("name")
                if name:
                    if name not in radio_groups:
                        radio_groups[name] = []
                    radio_groups[name].append(radio)
            
            # Select from the first group or specified group
            if radio_groups:
                group_name = list(radio_groups.keys())[0]
                group_buttons = radio_groups[group_name]
                
                if answer_index < len(group_buttons):
                    group_buttons[answer_index].click()
                    logger.info(f"Selected radio button {answer_index} from group '{group_name}'")
                    return True
                else:
                    logger.error(f"Answer index {answer_index} out of range")
                    return False
            else:
                logger.warning("No radio button groups found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to answer radio question: {e}")
            return False
    
    def answer_checkbox_question(self, checkbox_index: int = 0) -> bool:
        """
        Answer a checkbox question.
        
        Args:
            checkbox_index: Index of checkbox to select (0-based)
            
        Returns:
            bool: True if successful
        """
        try:
            checkboxes = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            
            if checkbox_index < len(checkboxes):
                checkboxes[checkbox_index].click()
                logger.info(f"Selected checkbox {checkbox_index}")
                return True
            else:
                logger.error(f"Checkbox index {checkbox_index} out of range")
                return False
                
        except Exception as e:
            logger.error(f"Failed to answer checkbox question: {e}")
            return False
    
    def fill_text_field(self, field_selector: str, text: str, selector_type: str = "css") -> bool:
        """
        Fill a text field.
        
        Args:
            field_selector: Element selector
            text: Text to enter
            selector_type: Type of selector
            
        Returns:
            bool: True if successful
        """
        by_map = {
            "css": By.CSS_SELECTOR,
            "id": By.ID,
            "name": By.NAME,
            "class": By.CLASS_NAME,
            "xpath": By.XPATH
        }
        
        by = by_map.get(selector_type.lower(), By.CSS_SELECTOR)
        return self.browser.fill_input(by, field_selector, text)
    
    def select_dropdown_option(self, select_selector: str, option_text: str, selector_type: str = "css") -> bool:
        """
        Select an option from a dropdown.
        
        Args:
            select_selector: Select element selector
            option_text: Text of option to select
            selector_type: Type of selector
            
        Returns:
            bool: True if successful
        """
        by_map = {
            "css": By.CSS_SELECTOR,
            "id": By.ID,
            "name": By.NAME,
            "class": By.CLASS_NAME,
            "xpath": By.XPATH
        }
        
        by = by_map.get(selector_type.lower(), By.CSS_SELECTOR)
        return self.browser.select_option(by, select_selector, option_text)
    
    def click_next_button(self) -> bool:
        """
        Click the next/submit button.
        
        Returns:
            bool: True if successful
        """
        # Common next button selectors
        next_selectors = [
            "input[type='submit']",
            "button[type='submit']",
            ".next",
            ".submit",
            "#next",
            "#submit",
            "[class*='next']",
            "[class*='submit']",
            "[id*='next']",
            "[id*='submit']"
        ]
        
        for selector in next_selectors:
            try:
                if self.browser.click_element(By.CSS_SELECTOR, selector):
                    logger.info(f"Clicked next button: {selector}")
                    return True
            except:
                continue
        
        logger.warning("No next button found")
        return False
    
    def handle_survey_page(self) -> bool:
        """
        Handle a single survey page by detecting and answering questions.
        
        Returns:
            bool: True if page handled successfully
        """
        try:
            # Wait for questions to load
            if not self.wait_for_survey_questions():
                logger.warning("No questions found on this page")
                return True  # Might be a completion page
            
            # Check for different question types and answer them
            success = True
            
            # Handle radio buttons
            radio_buttons = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            if radio_buttons:
                logger.info(f"Found {len(radio_buttons)} radio buttons")
                if not self.answer_radio_question(answer_index=random.randint(0, 2)):
                    success = False
            
            # Handle checkboxes
            checkboxes = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            if checkboxes:
                logger.info(f"Found {len(checkboxes)} checkboxes")
                # Select a random checkbox
                checkbox_index = random.randint(0, min(len(checkboxes) - 1, 2))
                if not self.answer_checkbox_question(checkbox_index):
                    success = False
            
            # Handle text fields
            text_fields = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], textarea")
            if text_fields:
                logger.info(f"Found {len(text_fields)} text fields")
                sample_texts = [
                    "This is a great survey!",
                    "I find this product interesting.",
                    "The quality is excellent.",
                    "I would recommend this to others.",
                    "Very satisfied with the experience."
                ]
                for i, field in enumerate(text_fields[:3]):  # Fill first 3 text fields
                    try:
                        field.clear()
                        field.send_keys(sample_texts[i % len(sample_texts)])
                        logger.info(f"Filled text field {i}")
                    except Exception as e:
                        logger.error(f"Failed to fill text field {i}: {e}")
                        success = False
            
            # Handle dropdowns
            selects = self.browser.driver.find_elements(By.CSS_SELECTOR, "select")
            if selects:
                logger.info(f"Found {len(selects)} dropdowns")
                for i, select in enumerate(selects):
                    try:
                        from selenium.webdriver.support.ui import Select
                        select_obj = Select(select)
                        if len(select_obj.options) > 1:
                            # Select a random option (skip first if it's "Please select")
                            option_index = random.randint(1, len(select_obj.options) - 1)
                            select_obj.select_by_index(option_index)
                            logger.info(f"Selected dropdown option {option_index}")
                    except Exception as e:
                        logger.error(f"Failed to select dropdown option: {e}")
                        success = False
            
            # Click next/submit button
            if not self.click_next_button():
                logger.warning("Could not find next button")
                success = False
            
            return success
            
        except Exception as e:
            logger.error(f"Error handling survey page: {e}")
            return False
    
    def complete_cpx_survey(self, max_pages: int = 10) -> bool:
        """
        Complete a CPX Research survey.
        
        Args:
            max_pages: Maximum number of pages to process
            
        Returns:
            bool: True if survey completed successfully
        """
        try:
            # Navigate to CPX Research
            if not self.navigate_to_cpx():
                logger.error("Failed to navigate to CPX Research")
                return False
            
            # Wait for page to load
            time.sleep(3)
            
            # Process survey pages
            page_count = 0
            while page_count < max_pages:
                logger.info(f"Processing survey page {page_count + 1}")
                
                # Take screenshot of current page
                self.browser.take_screenshot(f"cpx_survey_page_{page_count + 1}.png")
                
                # Handle the current page
                if not self.handle_survey_page():
                    logger.warning(f"Failed to handle page {page_count + 1}")
                
                # Wait for page transition
                time.sleep(random.uniform(2, 4))
                
                # Check if survey is complete
                current_url = self.browser.get_current_url()
                if "complete" in current_url.lower() or "thank" in current_url.lower():
                    logger.info("Survey appears to be complete")
                    break
                
                page_count += 1
            
            # Take final screenshot
            self.browser.take_screenshot("cpx_survey_complete.png")
            logger.info("CPX survey automation completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete CPX survey: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        self.start_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_browser()


def main():
    """
    Main function to run CPX survey automation.
    """
    print("CPX Research Survey Automation")
    print("=" * 35)
    print("This script will automate CPX Research surveys.")
    print("Make sure you have valid CPX Research credentials.")
    print()
    
    # Update user credentials if needed
    user_id = input("Enter your CPX user ID (or press Enter for default): ").strip()
    app_id = input("Enter your CPX app ID (or press Enter for default): ").strip()
    
    if user_id:
        CPXSurveyAutomation.user_id = user_id
    if app_id:
        CPXSurveyAutomation.app_id = app_id
    
    print(f"\nUsing CPX Research URL: {CPXSurveyAutomation.cpx_url}")
    print(f"User ID: {CPXSurveyAutomation.user_id}")
    print(f"App ID: {CPXSurveyAutomation.app_id}")
    print()
    
    confirm = input("Start CPX survey automation? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Automation cancelled.")
        return
    
    # Run the automation
    with CPXSurveyAutomation(headless=False) as cpx_automation:
        cpx_automation.complete_cpx_survey()


if __name__ == "__main__":
    main() 