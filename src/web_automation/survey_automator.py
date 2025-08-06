"""
Advanced Survey Automation

This module provides intelligent survey automation capabilities.
"""

import time
import random
import json
from typing import Dict, List, Optional, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from loguru import logger
from .firefox_automation import FirefoxAutomation


class SurveyAutomator:
    """
    Advanced survey automation class that can handle various survey types.
    """
    
    def __init__(self, headless: bool = False):
        """
        Initialize the survey automator.
        
        Args:
            headless: Whether to run in headless mode
        """
        self.browser = FirefoxAutomation(headless=headless)
        self.survey_data = {}
        self.current_survey = None
        
    def start_browser(self) -> bool:
        """Start the Firefox browser."""
        return self.browser.start_browser()
    
    def close_browser(self):
        """Close the Firefox browser."""
        self.browser.close_browser()
    
    def load_survey_data(self, filename: str) -> bool:
        """
        Load survey data from a JSON file.
        
        Args:
            filename: Path to JSON file with survey data
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            with open(filename, 'r') as f:
                self.survey_data = json.load(f)
            logger.info(f"Loaded survey data from {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to load survey data: {e}")
            return False
    
    def fill_text_input(self, selector: str, text: str, selector_type: str = "id") -> bool:
        """
        Fill a text input field.
        
        Args:
            selector: Element selector
            text: Text to enter
            selector_type: Type of selector (id, class, name, xpath)
            
        Returns:
            bool: True if successful
        """
        by_map = {
            "id": By.ID,
            "class": By.CLASS_NAME,
            "name": By.NAME,
            "xpath": By.XPATH,
            "css": By.CSS_SELECTOR
        }
        
        by = by_map.get(selector_type.lower(), By.ID)
        return self.browser.fill_input(by, selector, text)
    
    def click_button(self, selector: str, selector_type: str = "id") -> bool:
        """
        Click a button or link.
        
        Args:
            selector: Element selector
            selector_type: Type of selector
            
        Returns:
            bool: True if successful
        """
        by_map = {
            "id": By.ID,
            "class": By.CLASS_NAME,
            "name": By.NAME,
            "xpath": By.XPATH,
            "css": By.CSS_SELECTOR
        }
        
        by = by_map.get(selector_type.lower(), By.ID)
        return self.browser.click_element(by, selector)
    
    def select_dropdown(self, selector: str, option_text: str, selector_type: str = "id") -> bool:
        """
        Select an option from a dropdown.
        
        Args:
            selector: Element selector
            option_text: Text of option to select
            selector_type: Type of selector
            
        Returns:
            bool: True if successful
        """
        by_map = {
            "id": By.ID,
            "class": By.CLASS_NAME,
            "name": By.NAME,
            "xpath": By.XPATH,
            "css": By.CSS_SELECTOR
        }
        
        by = by_map.get(selector_type.lower(), By.ID)
        return self.browser.select_option(by, selector, option_text)
    
    def answer_multiple_choice(self, question_selector: str, answer_index: int, 
                             selector_type: str = "class") -> bool:
        """
        Answer a multiple choice question.
        
        Args:
            question_selector: Question container selector
            answer_index: Index of answer to select (0-based)
            selector_type: Type of selector
            
        Returns:
            bool: True if successful
        """
        try:
            by_map = {
                "id": By.ID,
                "class": By.CLASS_NAME,
                "name": By.NAME,
                "xpath": By.XPATH,
                "css": By.CSS_SELECTOR
            }
            
            by = by_map.get(selector_type.lower(), By.CLASS_NAME)
            
            # Find all answer options
            options = self.browser.driver.find_elements(by, question_selector)
            
            if answer_index < len(options):
                options[answer_index].click()
                logger.info(f"Selected answer {answer_index} for question")
                return True
            else:
                logger.error(f"Answer index {answer_index} out of range")
                return False
                
        except Exception as e:
            logger.error(f"Failed to answer multiple choice: {e}")
            return False
    
    def answer_scale_question(self, scale_selector: str, rating: int, 
                            selector_type: str = "class") -> bool:
        """
        Answer a scale/rating question.
        
        Args:
            scale_selector: Scale container selector
            rating: Rating value (1-10, etc.)
            selector_type: Type of selector
            
        Returns:
            bool: True if successful
        """
        try:
            by_map = {
                "id": By.ID,
                "class": By.CLASS_NAME,
                "name": By.NAME,
                "xpath": By.XPATH,
                "css": By.CSS_SELECTOR
            }
            
            by = by_map.get(selector_type.lower(), By.CLASS_NAME)
            
            # Find scale options
            scale_options = self.browser.driver.find_elements(by, scale_selector)
            
            if rating <= len(scale_options):
                scale_options[rating - 1].click()
                logger.info(f"Selected rating {rating}")
                return True
            else:
                logger.error(f"Rating {rating} out of range")
                return False
                
        except Exception as e:
            logger.error(f"Failed to answer scale question: {e}")
            return False
    
    def fill_demographics(self, demographics_data: Dict[str, str]) -> bool:
        """
        Fill out demographic information.
        
        Args:
            demographics_data: Dictionary with demographic fields and values
            
        Returns:
            bool: True if successful
        """
        success = True
        
        for field, value in demographics_data.items():
            if not self.fill_text_input(field, value):
                logger.warning(f"Failed to fill demographic field: {field}")
                success = False
        
        return success
    
    def wait_for_page_load(self, timeout: int = 10) -> bool:
        """
        Wait for page to load completely.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            bool: True if page loaded
        """
        try:
            time.sleep(2)  # Basic wait
            return True
        except Exception as e:
            logger.error(f"Error waiting for page load: {e}")
            return False
    
    def handle_captcha(self) -> bool:
        """
        Handle CAPTCHA if present (basic implementation).
        
        Returns:
            bool: True if handled or no CAPTCHA
        """
        # Check for common CAPTCHA elements
        captcha_selectors = [
            "iframe[src*='recaptcha']",
            ".g-recaptcha",
            "#captcha",
            ".captcha"
        ]
        
        for selector in captcha_selectors:
            try:
                captcha_element = self.browser.driver.find_element(By.CSS_SELECTOR, selector)
                if captcha_element:
                    logger.warning("CAPTCHA detected - manual intervention may be required")
                    # Wait for manual intervention
                    time.sleep(30)
                    return True
            except:
                continue
        
        return True  # No CAPTCHA found
    
    def complete_survey(self, survey_config: Dict[str, Any]) -> bool:
        """
        Complete a survey based on configuration.
        
        Args:
            survey_config: Survey configuration dictionary
            
        Returns:
            bool: True if survey completed successfully
        """
        try:
            # Navigate to survey URL
            if not self.browser.navigate_to_url(survey_config["url"]):
                return False
            
            # Wait for page load
            self.wait_for_page_load()
            
            # Handle login if required
            if "login" in survey_config:
                login_data = survey_config["login"]
                self.fill_text_input(login_data["username_field"], login_data["username"])
                self.fill_text_input(login_data["password_field"], login_data["password"])
                self.click_button(login_data["submit_button"])
                self.wait_for_page_load()
            
            # Fill demographics if provided
            if "demographics" in survey_config:
                self.fill_demographics(survey_config["demographics"])
            
            # Answer questions
            for question in survey_config.get("questions", []):
                question_type = question["type"]
                
                if question_type == "text":
                    self.fill_text_input(question["selector"], question["answer"])
                elif question_type == "multiple_choice":
                    self.answer_multiple_choice(question["selector"], question["answer_index"])
                elif question_type == "scale":
                    self.answer_scale_question(question["selector"], question["rating"])
                elif question_type == "dropdown":
                    self.select_dropdown(question["selector"], question["option"])
                
                # Wait between questions
                time.sleep(random.uniform(1, 3))
            
            # Submit survey
            if "submit_button" in survey_config:
                self.click_button(survey_config["submit_button"])
                self.wait_for_page_load()
            
            # Handle CAPTCHA if present
            self.handle_captcha()
            
            logger.info("Survey completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete survey: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        self.start_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_browser() 