#!/usr/bin/env python3
"""
CPX Research Survey Automation

This script provides specialized automation for CPX Research surveys.
"""

import time
import random
import json
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementNotInteractableException, TimeoutException
from loguru import logger
from src.web_automation.firefox_automation import FirefoxAutomation


class CPXSurveyAutomation:
    """
    Specialized automation for CPX Research surveys with hybrid vision/DOM approach.
    """
    
    def __init__(self, user_id: str, app_id: str, headless: bool = False):
        """
        Initialize CPX survey automation.
        
        Args:
            user_id: Your CPX Research user ID
            app_id: Your CPX Research app ID
            headless: Whether to run in headless mode
        """
        self.browser = FirefoxAutomation(headless=headless)
        self.cpx_url = "https://offers.cpx-research.com/index.php"
        self.user_id = user_id
        self.app_id = app_id
        
        # Load persona data
        self.persona = self.load_persona()
        
        # Vision analysis settings
        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
    def load_persona(self) -> dict:
        """
        Load persona data from persona.json file.
        
        Returns:
            dict: Persona data
        """
        try:
            persona_path = os.path.join(os.path.dirname(__file__), "persona.json")
            with open(persona_path, 'r') as f:
                persona_data = json.load(f)
            logger.info("Persona data loaded successfully")
            return persona_data
        except Exception as e:
            logger.error(f"Failed to load persona data: {e}")
            return {}
    
    def get_persona_value(self, key_path: str, default: str = "") -> str:
        """
        Get a value from persona data using dot notation.
        
        Args:
            key_path: Path to the value (e.g., "about_you.full_name")
            default: Default value if not found
            
        Returns:
            str: The value or default
        """
        try:
            keys = key_path.split('.')
            value = self.persona
            for key in keys:
                value = value.get(key, {})
            return str(value) if value else default
        except:
            return default
    
    def get_random_persona_text(self, category: str, field: str, fallback: str = "Good experience") -> str:
        """
        Get a random text response based on persona data.
        
        Args:
            category: Persona category (e.g., "survey_behavior")
            field: Field name (e.g., "product_feedback_general")
            fallback: Fallback text if not found
            
        Returns:
            str: Appropriate text response
        """
        try:
            value = self.persona.get(category, {}).get(field, fallback)
            if isinstance(value, list):
                return random.choice(value)
            return str(value)
        except:
            return fallback
    
    def get_persona_dropdown_option(self, category: str, field: str) -> str:
        """
        Get an appropriate dropdown option based on persona data.
        
        Args:
            category: Persona category
            field: Field name
            
        Returns:
            str: Appropriate option
        """
        try:
            value = self.persona.get(category, {}).get(field, "")
            if isinstance(value, list):
                return random.choice(value)
            return str(value)
        except:
            return ""
    
    def analyze_screenshot_vision(self, screenshot_path: str) -> dict:
        """
        Analyze screenshot using computer vision to detect interactive elements.
        
        Args:
            screenshot_path: Path to screenshot
            
        Returns:
            dict: Analysis results
        """
        try:
            # Load image
            image = cv2.imread(screenshot_path)
            if image is None:
                return {"error": "Could not load image"}
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect buttons and interactive elements
            analysis = {
                "buttons": self._detect_buttons(gray),
                "text_areas": self._detect_text_areas(gray),
                "checkboxes": self._detect_checkboxes(gray),
                "radio_buttons": self._detect_radio_buttons(gray),
                "dropdowns": self._detect_dropdowns(gray),
                "text_fields": self._detect_text_fields(gray)
            }
            
            logger.info(f"Vision analysis completed: {analysis}")
            return analysis
            
        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            return {"error": str(e)}
    
    def _detect_buttons(self, gray_image) -> list:
        """Detect button-like elements in the image."""
        try:
            # Edge detection
            edges = cv2.Canny(gray_image, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            buttons = []
            for contour in contours:
                # Filter by area and aspect ratio
                area = cv2.contourArea(contour)
                if 1000 < area < 50000:  # Reasonable button size
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 0.5 < aspect_ratio < 5:  # Button-like aspect ratio
                        buttons.append({
                            "type": "button",
                            "x": x, "y": y, "width": w, "height": h,
                            "center": (x + w//2, y + h//2)
                        })
            
            return buttons
        except Exception as e:
            logger.error(f"Button detection failed: {e}")
            return []
    
    def _detect_text_areas(self, gray_image) -> list:
        """Detect text input areas."""
        try:
            # Use morphological operations to find rectangular areas
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 5))
            morph = cv2.morphologyEx(gray_image, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            text_areas = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if 500 < area < 20000:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 2 < aspect_ratio < 10:  # Text field aspect ratio
                        text_areas.append({
                            "type": "text_area",
                            "x": x, "y": y, "width": w, "height": h,
                            "center": (x + w//2, y + h//2)
                        })
            
            return text_areas
        except Exception as e:
            logger.error(f"Text area detection failed: {e}")
            return []
    
    def _detect_checkboxes(self, gray_image) -> list:
        """Detect checkbox elements."""
        try:
            # Look for small square elements
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            morph = cv2.morphologyEx(gray_image, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            checkboxes = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if 100 < area < 2000:  # Checkbox size
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 0.8 < aspect_ratio < 1.2:  # Square-like
                        checkboxes.append({
                            "type": "checkbox",
                            "x": x, "y": y, "width": w, "height": h,
                            "center": (x + w//2, y + h//2)
                        })
            
            return checkboxes
        except Exception as e:
            logger.error(f"Checkbox detection failed: {e}")
            return []
    
    def _detect_radio_buttons(self, gray_image) -> list:
        """Detect radio button elements."""
        try:
            # Similar to checkboxes but look for circular patterns
            circles = cv2.HoughCircles(
                gray_image, cv2.HOUGH_GRADIENT, dp=1, minDist=20,
                param1=50, param2=30, minRadius=5, maxRadius=30
            )
            
            radio_buttons = []
            if circles is not None:
                for circle in circles[0]:
                    x, y, radius = circle
                    radio_buttons.append({
                        "type": "radio_button",
                        "x": int(x - radius), "y": int(y - radius),
                        "width": int(2 * radius), "height": int(2 * radius),
                        "center": (int(x), int(y))
                    })
            
            return radio_buttons
        except Exception as e:
            logger.error(f"Radio button detection failed: {e}")
            return []
    
    def _detect_dropdowns(self, gray_image) -> list:
        """Detect dropdown elements."""
        try:
            # Look for rectangular elements with dropdown indicators
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 10))
            morph = cv2.morphologyEx(gray_image, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            dropdowns = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if 500 < area < 15000:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 1.5 < aspect_ratio < 8:  # Dropdown aspect ratio
                        dropdowns.append({
                            "type": "dropdown",
                            "x": x, "y": y, "width": w, "height": h,
                            "center": (x + w//2, y + h//2)
                        })
            
            return dropdowns
        except Exception as e:
            logger.error(f"Dropdown detection failed: {e}")
            return []
    
    def _detect_text_fields(self, gray_image) -> list:
        """Detect text input fields."""
        try:
            # Similar to text areas but smaller
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
            morph = cv2.morphologyEx(gray_image, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            text_fields = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if 200 < area < 10000:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 3 < aspect_ratio < 15:  # Text field aspect ratio
                        text_fields.append({
                            "type": "text_field",
                            "x": x, "y": y, "width": w, "height": h,
                            "center": (x + w//2, y + h//2)
                        })
            
            return text_fields
        except Exception as e:
            logger.error(f"Text field detection failed: {e}")
            return []
    
    def click_element_by_vision(self, element_type: str, index: int = 0) -> bool:
        """
        Click an element detected by vision analysis.
        
        Args:
            element_type: Type of element to click
            index: Index of element to click
            
        Returns:
            bool: True if successful
        """
        try:
            # Take screenshot
            screenshot_path = os.path.join(self.screenshot_dir, "current_page.png")
            self.browser.take_screenshot(screenshot_path)
            
            # Analyze screenshot
            analysis = self.analyze_screenshot_vision(screenshot_path)
            
            if "error" in analysis:
                logger.error(f"Vision analysis failed: {analysis['error']}")
                return False
            
            # Find elements of the specified type
            elements = analysis.get(element_type, [])
            if not elements or index >= len(elements):
                logger.warning(f"No {element_type} elements found or index out of range")
                return False
            
            # Get element coordinates
            element = elements[index]
            center_x, center_y = element["center"]
            
            # Click using ActionChains for better reliability
            actions = ActionChains(self.browser.driver)
            actions.move_by_offset(center_x, center_y)
            actions.click()
            actions.perform()
            
            logger.info(f"Clicked {element_type} at coordinates ({center_x}, {center_y})")
            return True
            
        except Exception as e:
            logger.error(f"Vision-based clicking failed: {e}")
            return False
    
    def fill_text_field_by_vision(self, text: str, index: int = 0) -> bool:
        """
        Fill a text field detected by vision analysis.
        
        Args:
            text: Text to enter
            index: Index of text field to fill
            
        Returns:
            bool: True if successful
        """
        try:
            # Take screenshot
            screenshot_path = os.path.join(self.screenshot_dir, "current_page.png")
            self.browser.take_screenshot(screenshot_path)
            
            # Analyze screenshot
            analysis = self.analyze_screenshot_vision(screenshot_path)
            
            if "error" in analysis:
                logger.error(f"Vision analysis failed: {analysis['error']}")
                return False
            
            # Find text fields
            text_fields = analysis.get("text_fields", [])
            if not text_fields or index >= len(text_fields):
                logger.warning(f"No text fields found or index out of range")
                return False
            
            # Get element coordinates
            element = text_fields[index]
            center_x, center_y = element["center"]
            
            # Click to focus and type
            actions = ActionChains(self.browser.driver)
            actions.move_by_offset(center_x, center_y)
            actions.click()
            actions.send_keys(text)
            actions.perform()
            
            logger.info(f"Filled text field at coordinates ({center_x}, {center_y}) with: {text}")
            return True
            
        except Exception as e:
            logger.error(f"Vision-based text filling failed: {e}")
            return False
        
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
    
    def answer_radio_question_with_persona(self) -> bool:
        """
        Answer radio button questions based on persona data.
        
        Returns:
            bool: True if successful
        """
        try:
            radio_buttons = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            if not radio_buttons:
                logger.warning("No radio buttons found")
                return False
            
            # Get the parent element to find question text
            if radio_buttons:
                parent = radio_buttons[0].find_element(By.XPATH, "./..")
                question_text = parent.text.lower() if parent else ""
                
                # Handle specific survey questions
                if any(word in question_text for word in ["united states", "country", "live in"]):
                    # For country questions, select "Yes, I am from the United States"
                    answer_index = 0  # First option is usually "Yes"
                    logger.info("Detected country question - selecting United States")
                elif any(word in question_text for word in ["satisfied", "happy", "pleased"]):
                    # Choose positive responses for satisfaction questions
                    answer_index = min(3, len(radio_buttons) - 1)  # Usually last option is most positive
                elif any(word in question_text for word in ["income", "salary", "earnings"]):
                    # Choose higher income options
                    answer_index = min(2, len(radio_buttons) - 1)
                elif any(word in question_text for word in ["technology", "tech", "digital"]):
                    # Choose positive responses for technology questions
                    answer_index = min(2, len(radio_buttons) - 1)
                elif any(word in question_text for word in ["health", "fitness", "exercise"]):
                    # Choose moderate to positive responses for health questions
                    answer_index = min(2, len(radio_buttons) - 1)
                elif any(word in question_text for word in ["shopping", "purchase", "buy"]):
                    # Choose positive responses for shopping questions
                    answer_index = min(2, len(radio_buttons) - 1)
                else:
                    # Default to first option for neutral questions
                    answer_index = 0
                
                if answer_index < len(radio_buttons):
                    # Try to scroll to the element first
                    try:
                        self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", radio_buttons[answer_index])
                        time.sleep(0.5)
                    except:
                        pass
                    
                    radio_buttons[answer_index].click()
                    logger.info(f"Clicked radio button {answer_index} based on persona analysis")
                    return True
                else:
                    logger.warning("Radio button index out of range")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to answer radio question with persona: {e}")
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
            "[id*='submit']",
            "button[class*='arrow']",
            "button[class*='next']",
            "button[class*='continue']"
        ]
        
        for selector in next_selectors:
            try:
                elements = self.browser.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        # Scroll to element first
                        self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        time.sleep(0.5)
                        element.click()
                    logger.info(f"Clicked next button: {selector}")
                    return True
            except:
                continue
        
        # Try vision-based approach for circular buttons
        try:
            screenshot_path = os.path.join(self.screenshot_dir, "next_button.png")
            self.browser.take_screenshot(screenshot_path)
            
            analysis = self.analyze_screenshot_vision(screenshot_path)
            buttons = analysis.get("buttons", [])
            
            if buttons:
                # Look for circular buttons (usually next buttons)
                for button in buttons:
                    # Check if it's roughly circular (width ≈ height)
                    if abs(button["width"] - button["height"]) < 20:
                        center_x, center_y = button["center"]
                        
                        # Scroll to button area
                        self.browser.driver.execute_script(f"window.scrollTo(0, {center_y - 100});")
                        time.sleep(0.5)
                        
                        # Click using ActionChains
                        actions = ActionChains(self.browser.driver)
                        actions.move_by_offset(center_x, center_y)
                        actions.click()
                        actions.perform()
                        
                        logger.info(f"Clicked circular next button via vision at coordinates ({center_x}, {center_y})")
                        return True
        except Exception as e:
            logger.warning(f"Vision-based next button approach failed: {e}")
        
        logger.warning("No next button found")
        return False
    
    def click_next_button_enhanced(self) -> bool:
        """
        Enhanced next button clicking with multiple approaches.
        
        Returns:
            bool: True if successful
        """
        try:
            # Approach 1: Look for common next button selectors
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
                "[id*='submit']",
                "button:contains('Next')",
                "button:contains('Continue')",
                "button:contains('Submit')"
            ]
            
            for selector in next_selectors:
                try:
                    elements = self.browser.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            # Scroll to element
                            self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                            time.sleep(0.5)
                            element.click()
                            logger.info(f"Clicked next button: {selector}")
                            return True
                except:
                    continue
            
            # Approach 2: Look for buttons with arrow icons or next text
            try:
                arrow_buttons = self.browser.driver.find_elements(By.XPATH, "//button[contains(@class, 'arrow') or contains(@class, 'next') or contains(text(), 'Next') or contains(text(), 'Continue')]")
                
                for button in arrow_buttons:
                    if button.is_displayed() and button.is_enabled():
                        self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(0.5)
                        button.click()
                        logger.info(f"Clicked arrow/next button: {button.text}")
                        return True
            except Exception as e:
                logger.warning(f"Arrow button approach failed: {e}")
            
            # Approach 3: Vision-based button detection
            try:
                screenshot_path = os.path.join(self.screenshot_dir, "next_button.png")
                self.browser.take_screenshot(screenshot_path)
                
                analysis = self.analyze_screenshot_vision(screenshot_path)
                buttons = analysis.get("buttons", [])
                
                if buttons:
                    # Try to find the most likely next button (usually at bottom)
                    next_button = None
                    for button in buttons:
                        if button["y"] > 800:  # Usually at bottom of page
                            next_button = button
                            break
                    
                    if next_button:
                        center_x, center_y = next_button["center"]
                        
                        # Scroll to button area
                        self.browser.driver.execute_script(f"window.scrollTo(0, {center_y - 100});")
                        time.sleep(0.5)
                        
                        # Click using ActionChains
                        actions = ActionChains(self.browser.driver)
                        actions.move_by_offset(center_x, center_y)
                        actions.click()
                        actions.perform()
                        
                        logger.info(f"Clicked next button via vision at coordinates ({center_x}, {center_y})")
                        return True
            except Exception as e:
                logger.warning(f"Vision-based next button approach failed: {e}")
            
            logger.warning("No next button found")
            return False
            
        except Exception as e:
            logger.error(f"Enhanced next button clicking failed: {e}")
            return False
    
    def handle_survey_page(self) -> bool:
        """
        Handle a single survey page using hybrid vision/DOM approach.
        
        Returns:
            bool: True if page handled successfully
        """
        try:
            # Wait for questions to load
            if not self.wait_for_survey_questions():
                logger.warning("No questions found on this page")
                return True  # Might be a completion page
            
            # Check for country selection question first
            if self.handle_country_selection():
                logger.info("Successfully handled country selection")
                # Click next button after country selection
                time.sleep(1)
                if not self.click_next_button():
                    # Try vision-based button clicking
                    logger.info("Trying vision-based next button detection")
                    if not self.click_element_by_vision("buttons", 0):
                        logger.warning("Could not find next button")
                        return False
                return True
            
            # Take screenshot for vision analysis
            screenshot_path = os.path.join(self.screenshot_dir, "current_page.png")
            self.browser.take_screenshot(screenshot_path)
            
            # Analyze page using vision
            vision_analysis = self.analyze_screenshot_vision(screenshot_path)
            
            success = True
            
            # Handle radio buttons (try DOM first, then vision)
            radio_buttons = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            if radio_buttons:
                logger.info(f"Found {len(radio_buttons)} radio buttons via DOM")
                if not self.answer_radio_question_with_persona():
                    # Fallback to vision-based clicking
                    logger.info("Trying vision-based radio button selection")
                    if not self.click_element_by_vision("radio_buttons", 0):
                        success = False
            elif vision_analysis.get("radio_buttons"):
                logger.info("Using vision-based radio button detection")
                if not self.click_element_by_vision("radio_buttons", 0):
                    success = False
            
            # Handle checkboxes
            checkboxes = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            if checkboxes:
                logger.info(f"Found {len(checkboxes)} checkboxes via DOM")
                checkbox_index = random.randint(0, min(len(checkboxes) - 1, 2))
                if not self.answer_checkbox_question(checkbox_index):
                    success = False
            elif vision_analysis.get("checkboxes"):
                logger.info("Using vision-based checkbox detection")
                if not self.click_element_by_vision("checkboxes", 0):
                    success = False
            
            # Handle text fields with persona data
            text_fields = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], textarea")
            if text_fields:
                logger.info(f"Found {len(text_fields)} text fields via DOM")
                
                # Persona-based text responses
                persona_texts = [
                    self.get_random_persona_text("survey_behavior", "product_feedback_general", "I appreciate products that are user-friendly and integrate well with other devices."),
                    self.get_random_persona_text("survey_behavior", "service_feedback_general", "Customer service should be responsive and knowledgeable."),
                    self.get_random_persona_text("survey_behavior", "website_experience_general", "I prefer websites that are easy to navigate and mobile-friendly."),
                    f"I'm {self.get_persona_value('about_you.full_name', 'a satisfied customer')} and I find this experience very positive.",
                    self.get_random_persona_text("survey_behavior", "satisfaction_with_life", "Very satisfied with the overall experience.")
                ]
                
                for i, field in enumerate(text_fields[:5]):
                    response_text = persona_texts[i % len(persona_texts)]
                    try:
                        field.clear()
                        field.send_keys(response_text)
                        logger.info(f"Filled text field {i} with persona-based response")
                    except ElementNotInteractableException:
                        # Try vision-based text filling
                        logger.info(f"Trying vision-based text filling for field {i}")
                        if not self.fill_text_field_by_vision(response_text, i):
                            success = False
                    except Exception as e:
                        logger.error(f"Failed to fill text field {i}: {e}")
                        success = False
            elif vision_analysis.get("text_fields"):
                logger.info("Using vision-based text field detection")
                persona_text = self.get_random_persona_text("survey_behavior", "product_feedback_general")
                if not self.fill_text_field_by_vision(persona_text, 0):
                    success = False
            
            # Handle dropdowns with persona data
            selects = self.browser.driver.find_elements(By.CSS_SELECTOR, "select")
            if selects:
                logger.info(f"Found {len(selects)} dropdowns via DOM")
                
                # Persona-based dropdown options
                persona_options = [
                    self.get_persona_dropdown_option("about_you", "gender"),
                    self.get_persona_dropdown_option("about_you", "state"),
                    self.get_persona_dropdown_option("about_you", "ethnicity"),
                    self.get_persona_dropdown_option("work", "employment_status"),
                    self.get_persona_dropdown_option("home", "marital_status"),
                    self.get_persona_dropdown_option("about_you", "age"),
                    self.get_persona_dropdown_option("work", "personal_income_before_taxes"),
                    self.get_persona_dropdown_option("home", "household_income")
                ]
                
                for i, select in enumerate(selects):
                    try:
                        from selenium.webdriver.support.ui import Select
                        select_obj = Select(select)
                        if len(select_obj.options) > 1:
                            # Try to match persona data first
                            if i < len(persona_options) and persona_options[i]:
                                # Look for matching option
                                for option in select_obj.options:
                                    if persona_options[i].lower() in option.text.lower():
                                        select_obj.select_by_visible_text(option.text)
                                        logger.info(f"Selected persona-based dropdown option: {option.text}")
                                        break
                                else:
                                    # Fallback to random selection
                                    option_index = random.randint(1, len(select_obj.options) - 1)
                                    select_obj.select_by_index(option_index)
                                    logger.info(f"Selected random dropdown option {option_index}")
                            else:
                                # Fallback to random selection
                                option_index = random.randint(1, len(select_obj.options) - 1)
                                select_obj.select_by_index(option_index)
                                logger.info(f"Selected random dropdown option {option_index}")
                    except Exception as e:
                        logger.error(f"Failed to select dropdown option: {e}")
                        success = False
            elif vision_analysis.get("dropdowns"):
                logger.info("Using vision-based dropdown detection")
                if not self.click_element_by_vision("dropdowns", 0):
                    success = False
            
            # Click next/submit button (try DOM first, then vision)
            if not self.click_next_button():
                # Try vision-based button clicking
                logger.info("Trying vision-based next button detection")
                if not self.click_element_by_vision("buttons", 0):
                    logger.warning("Could not find next button")
                    success = False
            
            return success
            
        except Exception as e:
            logger.error(f"Error handling survey page: {e}")
        return False
    
    def handle_country_selection(self) -> bool:
        """
        Handle the specific country selection question.
        
        Returns:
            bool: True if successful
        """
        try:
            # Look for the specific country question
            page_text = self.browser.driver.page_source.lower()
            
            if "united states" in page_text or "country" in page_text:
                logger.info("Detected country selection question")
                
                # Try multiple approaches to find and click the "Yes" option
                
                # Approach 1: Look for buttons with "United States" or "Yes" text
                try:
                    buttons = self.browser.driver.find_elements(By.XPATH, "//*[contains(text(), 'United States') or contains(text(), 'Yes')]")
                    
                    for button in buttons:
                        button_text = button.text.lower()
                        if "united states" in button_text or "yes" in button_text:
                            # Scroll to button first
                            self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                            time.sleep(0.5)
                            button.click()
                            logger.info(f"Clicked button: {button.text}")
                            return True
                except Exception as e:
                    logger.warning(f"Button approach failed: {e}")
                
                # Approach 2: Look for clickable elements with specific text
                try:
                    clickable_elements = self.browser.driver.find_elements(By.XPATH, "//*[contains(text(), 'Yes, I am from the United States')]")
                    
                    for element in clickable_elements:
                        self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        time.sleep(0.5)
                        element.click()
                        logger.info(f"Clicked element: {element.text}")
                        return True
                except Exception as e:
                    logger.warning(f"Clickable element approach failed: {e}")
                
                # Approach 3: Try radio buttons (fallback)
                try:
                    radio_buttons = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                    if radio_buttons:
                        # Select the first radio button (usually "Yes")
                        self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", radio_buttons[0])
                        time.sleep(0.5)
                        radio_buttons[0].click()
                        logger.info("Clicked first radio button for country selection")
                        return True
                except Exception as e:
                    logger.warning(f"Radio button approach failed: {e}")
                
                # Approach 4: Use vision-based detection
                try:
                    screenshot_path = os.path.join(self.screenshot_dir, "country_selection.png")
                    self.browser.take_screenshot(screenshot_path)
                    
                    # Analyze for buttons
                    analysis = self.analyze_screenshot_vision(screenshot_path)
                    buttons = analysis.get("buttons", [])
                    
                    if buttons:
                        # Click the first detected button
                        element = buttons[0]
                        center_x, center_y = element["center"]
                        
                        # Scroll to button area
                        self.browser.driver.execute_script(f"window.scrollTo(0, {center_y - 100});")
                        time.sleep(0.5)
                        
                        # Click using ActionChains
                        actions = ActionChains(self.browser.driver)
                        actions.move_by_offset(center_x, center_y)
                        actions.click()
                        actions.perform()
                        
                        logger.info(f"Clicked button via vision at coordinates ({center_x}, {center_y})")
                        return True
                except Exception as e:
                    logger.warning(f"Vision-based approach failed: {e}")
                
                logger.error("All country selection approaches failed")
                return False
            
            return False
            
        except Exception as e:
            logger.error(f"Error in handle_country_selection: {e}")
            return False
    
    def complete_cpx_survey(self, max_pages: int = 20) -> bool:
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
            time.sleep(5)
            
            # Process survey pages
            page_count = 0
            while page_count < max_pages:
                logger.info(f"Processing survey page {page_count + 1}")
                
                # Take screenshot of current page
                screenshot_path = os.path.join(self.screenshot_dir, f"cpx_survey_page_{page_count + 1}.png")
                self.browser.take_screenshot(screenshot_path)
                
                # Handle the current page
                if not self.handle_survey_page():
                    logger.warning(f"Failed to handle page {page_count + 1}")
                
                # Wait for page transition with random delay
                time.sleep(random.uniform(3, 6))
                
                # Check if survey is complete
                current_url = self.browser.get_current_url()
                if "complete" in current_url.lower() or "thank" in current_url.lower():
                    logger.info("Survey appears to be complete")
                    break
                
                page_count += 1
            
            # Take final screenshot
            final_screenshot_path = os.path.join(self.screenshot_dir, "cpx_survey_complete.png")
            self.browser.take_screenshot(final_screenshot_path)
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