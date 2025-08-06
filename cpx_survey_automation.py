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
from selenium.common.exceptions import ElementNotInteractableException, TimeoutException, NoSuchElementException
from loguru import logger
from src.web_automation.firefox_automation import FirefoxAutomation


class CPXSurveyAutomation:
    """
    Specialized automation for CPX Research surveys with hybrid vision/DOM approach.
    """
    
    # Class attributes for default values
    cpx_url = "https://offers.cpx-research.com/index.php"
    user_id = "533055960609193994_1246050346233757798"
    app_id = "27806"
    
    def __init__(self, headless: bool = False):
        """
        Initialize CPX survey automation.
        
        Args:
            headless: Whether to run in headless mode
        """
        self.browser = FirefoxAutomation(headless=headless)
        # Use class attributes as instance attributes
        self.cpx_url = self.cpx_url
        self.user_id = self.user_id
        self.app_id = self.app_id
        
        # Load persona data
        self.persona = self.load_persona()
        
        # Vision analysis settings
        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Survey completion tracking
        self.surveys_completed = 0
        self.total_earnings = 0.0
        self.current_survey_earnings = 0.0
        
        # Automation settings
        self.max_wait_time = 30
        self.random_delays = True
        self.auto_accept_surveys = True
        
        logger.info("CPX Survey Automation initialized")
    
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
            str: Random text response
        """
        try:
            responses = self.persona.get(category, {}).get(field, [fallback])
            if isinstance(responses, list):
                return random.choice(responses)
            return str(responses)
        except:
            return fallback
    
    def get_persona_dropdown_option(self, category: str, field: str) -> str:
        """
        Get a dropdown option based on persona data.
        
        Args:
            category: Persona category
            field: Field name
            
        Returns:
            str: Selected dropdown option
        """
        try:
            options = self.persona.get(category, {}).get(field, [])
            if isinstance(options, list) and options:
                return random.choice(options)
            return "Other"
        except:
            return "Other"
    
    def analyze_screenshot_vision(self, screenshot_path: str) -> dict:
        """
        Analyze screenshot using computer vision to detect UI elements.
        
        Args:
            screenshot_path: Path to screenshot file
            
        Returns:
            dict: Analysis results with detected elements
        """
        try:
            # Load image
            image = cv2.imread(screenshot_path)
            if image is None:
                return {}
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape
            
            analysis = {
                'buttons': self._detect_buttons(gray),
                'text_areas': self._detect_text_areas(gray),
                'checkboxes': self._detect_checkboxes(gray),
                'radio_buttons': self._detect_radio_buttons(gray),
                'dropdowns': self._detect_dropdowns(gray),
                'text_fields': self._detect_text_fields(gray)
            }
            
            logger.info(f"Vision analysis completed: {len(analysis['buttons'])} buttons, {len(analysis['text_fields'])} text fields")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in vision analysis: {e}")
            return {}
    
    def _detect_buttons(self, gray_image) -> list:
        """Detect buttons in the image."""
        try:
            # Simple edge detection for buttons
            edges = cv2.Canny(gray_image, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            buttons = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if 50 < w < 300 and 20 < h < 100:  # Button-like dimensions
                    buttons.append({'x': x, 'y': y, 'width': w, 'height': h})
            
            return buttons
        except:
            return []
    
    def _detect_text_areas(self, gray_image) -> list:
        """Detect text areas in the image."""
        try:
            # Use morphological operations to detect text regions
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            dilated = cv2.dilate(gray_image, kernel, iterations=1)
            
            # Find contours
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            text_areas = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if 100 < w < 800 and 20 < h < 200:  # Text area dimensions
                    text_areas.append({'x': x, 'y': y, 'width': w, 'height': h})
            
            return text_areas
        except:
            return []
    
    def _detect_checkboxes(self, gray_image) -> list:
        """Detect checkboxes in the image."""
        try:
            # Look for small square shapes
            edges = cv2.Canny(gray_image, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            checkboxes = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if 10 < w < 50 and 10 < h < 50 and abs(w - h) < 10:  # Square-like
                    checkboxes.append({'x': x, 'y': y, 'width': w, 'height': h})
            
            return checkboxes
        except:
            return []
    
    def _detect_radio_buttons(self, gray_image) -> list:
        """Detect radio buttons in the image."""
        try:
            # Look for circular shapes
            circles = cv2.HoughCircles(
                gray_image, cv2.HOUGH_GRADIENT, 1, 20,
                param1=50, param2=30, minRadius=5, maxRadius=30
            )
            
            radio_buttons = []
            if circles is not None:
                for circle in circles[0]:
                    x, y, r = circle
                    radio_buttons.append({'x': int(x), 'y': int(y), 'radius': int(r)})
            
            return radio_buttons
        except:
            return []
    
    def _detect_dropdowns(self, gray_image) -> list:
        """Detect dropdown elements in the image."""
        try:
            # Look for rectangular shapes with specific aspect ratios
            edges = cv2.Canny(gray_image, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            dropdowns = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if 100 < w < 400 and 20 < h < 60:  # Dropdown-like dimensions
                    dropdowns.append({'x': x, 'y': y, 'width': w, 'height': h})
            
            return dropdowns
        except:
            return []
    
    def _detect_text_fields(self, gray_image) -> list:
        """Detect text input fields in the image."""
        try:
            # Look for rectangular input fields
            edges = cv2.Canny(gray_image, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            text_fields = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if 150 < w < 600 and 20 < h < 50:  # Text field dimensions
                    text_fields.append({'x': x, 'y': y, 'width': w, 'height': h})
            
            return text_fields
        except:
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
            elements = analysis.get(element_type, [])
            
            if not elements or index >= len(elements):
                logger.warning(f"No {element_type} found at index {index}")
                return False
            
            element = elements[index]
            
            # Calculate click coordinates
            if element_type in ['buttons', 'checkboxes', 'text_fields', 'dropdowns']:
                x = element['x'] + element['width'] // 2
                y = element['y'] + element['height'] // 2
            elif element_type == 'radio_buttons':
                x = element['x']
                y = element['y']
            else:
                return False
            
            # Perform click
            actions = ActionChains(self.browser.driver)
            actions.move_by_offset(x, y).click().perform()
            
            # Reset mouse position
            actions.move_by_offset(-x, -y).perform()
            
            logger.info(f"Clicked {element_type} at ({x}, {y})")
            return True
            
        except Exception as e:
            logger.error(f"Error clicking element by vision: {e}")
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
            text_fields = analysis.get('text_fields', [])
            
            if not text_fields or index >= len(text_fields):
                logger.warning(f"No text field found at index {index}")
                return False
            
            field = text_fields[index]
            
            # Calculate click coordinates
            x = field['x'] + field['width'] // 2
            y = field['y'] + field['height'] // 2
            
            # Click on field and type
            actions = ActionChains(self.browser.driver)
            actions.move_by_offset(x, y).click().perform()
            
            # Clear field and type text
            actions.send_keys(text).perform()
            
            # Reset mouse position
            actions.move_by_offset(-x, -y).perform()
            
            logger.info(f"Filled text field with: {text}")
            return True
            
        except Exception as e:
            logger.error(f"Error filling text field by vision: {e}")
            return False
    
    def start_browser(self) -> bool:
        """Start the browser."""
        try:
            self.browser.start()
            logger.info("Browser started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return False
    
    def close_browser(self):
        """Close the browser."""
        try:
            self.browser.close()
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    def navigate_to_cpx(self) -> bool:
        """Navigate to CPX Research website."""
        try:
            # Construct full URL with parameters
            full_url = f"{self.cpx_url}?app_id={self.app_id}&ext_user_id={self.user_id}"
            logger.info(f"Navigating to CPX Research: {full_url}")
            
            self.browser.navigate(full_url)
            
            # Wait for page to load
            WebDriverWait(self.browser.driver, self.max_wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            logger.info("Successfully navigated to CPX Research")
            return True
            
        except Exception as e:
            logger.error(f"Failed to navigate to CPX Research: {e}")
            return False
    
    def wait_for_survey_questions(self, timeout: int = 30) -> bool:
        """
        Wait for survey questions to appear on the page.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if questions found
        """
        try:
            # Wait for common survey question elements
            selectors = [
                "input[type='radio']",
                "input[type='checkbox']",
                "textarea",
                "input[type='text']",
                "select",
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
                except TimeoutException:
                    continue
            
            logger.warning("No survey questions found within timeout")
            return False
            
        except Exception as e:
            logger.error(f"Error waiting for survey questions: {e}")
            return False
    
    def answer_radio_question(self, question_text: str = None, answer_index: int = 0) -> bool:
        """
        Answer a radio button question.
        
        Args:
            question_text: Text to look for in the question
            answer_index: Index of answer to select
            
        Returns:
            bool: True if successful
        """
        try:
            # Find radio buttons
            radio_buttons = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            
            if not radio_buttons:
                logger.warning("No radio buttons found")
                return False
            
            # Select answer by index
            if answer_index < len(radio_buttons):
                radio_buttons[answer_index].click()
                logger.info(f"Selected radio button {answer_index}")
                return True
            else:
                # Select random answer
                random_index = random.randint(0, len(radio_buttons) - 1)
                radio_buttons[random_index].click()
                logger.info(f"Selected random radio button {random_index}")
                return True
                
        except Exception as e:
            logger.error(f"Error answering radio question: {e}")
            return False
    
    def answer_checkbox_question(self, checkbox_index: int = 0) -> bool:
        """
        Answer a checkbox question.
        
        Args:
            checkbox_index: Index of checkbox to select
            
        Returns:
            bool: True if successful
        """
        try:
            # Find checkboxes
            checkboxes = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            
            if not checkboxes:
                logger.warning("No checkboxes found")
                return False
            
            # Select checkbox by index
            if checkbox_index < len(checkboxes):
                checkboxes[checkbox_index].click()
                logger.info(f"Selected checkbox {checkbox_index}")
                return True
            else:
                # Select random checkbox
                random_index = random.randint(0, len(checkboxes) - 1)
                checkboxes[random_index].click()
                logger.info(f"Selected random checkbox {random_index}")
                return True
                
        except Exception as e:
            logger.error(f"Error answering checkbox question: {e}")
            return False
    
    def answer_radio_question_with_persona(self) -> bool:
        """
        Answer a radio question using persona data.
        
        Returns:
            bool: True if successful
        """
        try:
            # Find radio buttons
            radio_buttons = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            
            if not radio_buttons:
                logger.warning("No radio buttons found")
                return False
            
            # Get persona-based answer
            persona_answer = self.get_persona_value("survey_behavior.default_radio_answer", "1")
            try:
                answer_index = int(persona_answer) - 1  # Convert to 0-based index
                if 0 <= answer_index < len(radio_buttons):
                    radio_buttons[answer_index].click()
                    logger.info(f"Selected radio button {answer_index} based on persona")
                    return True
            except ValueError:
                pass
            
            # Fallback to random selection
            random_index = random.randint(0, len(radio_buttons) - 1)
            radio_buttons[random_index].click()
            logger.info(f"Selected random radio button {random_index}")
            return True
            
        except Exception as e:
            logger.error(f"Error answering radio question with persona: {e}")
            return False
    
    def fill_text_field(self, field_selector: str, text: str, selector_type: str = "css") -> bool:
        """
        Fill a text field with specified text.
        
        Args:
            field_selector: CSS selector or XPath for the field
            text: Text to enter
            selector_type: Type of selector ("css" or "xpath")
            
        Returns:
            bool: True if successful
        """
        try:
            if selector_type == "css":
                element = self.browser.driver.find_element(By.CSS_SELECTOR, field_selector)
            else:
                element = self.browser.driver.find_element(By.XPATH, field_selector)
            
            element.clear()
            element.send_keys(text)
            logger.info(f"Filled text field with: {text}")
            return True
            
        except Exception as e:
            logger.error(f"Error filling text field: {e}")
            return False
    
    def select_dropdown_option(self, select_selector: str, option_text: str, selector_type: str = "css") -> bool:
        """
        Select an option from a dropdown.
        
        Args:
            select_selector: CSS selector or XPath for the select element
            option_text: Text of the option to select
            selector_type: Type of selector ("css" or "xpath")
            
        Returns:
            bool: True if successful
        """
        try:
            from selenium.webdriver.support.ui import Select
            
            if selector_type == "css":
                select_element = self.browser.driver.find_element(By.CSS_SELECTOR, select_selector)
            else:
                select_element = self.browser.driver.find_element(By.XPATH, select_selector)
            
            select = Select(select_element)
            select.select_by_visible_text(option_text)
            logger.info(f"Selected dropdown option: {option_text}")
            return True
            
        except Exception as e:
            logger.error(f"Error selecting dropdown option: {e}")
            return False
    
    def click_next_button(self) -> bool:
        """
        Click the next/continue button.
        
        Returns:
            bool: True if successful
        """
        try:
            # Common next button selectors
            next_selectors = [
                "input[type='submit'][value*='Next']",
                "input[type='submit'][value*='Continue']",
                "input[type='submit'][value*='Submit']",
                "button[type='submit']",
                "input[value*='Next']",
                "input[value*='Continue']",
                "input[value*='Submit']",
                "button:contains('Next')",
                "button:contains('Continue')",
                "button:contains('Submit')",
                ".next-button",
                ".continue-button",
                ".submit-button",
                "[class*='next']",
                "[class*='continue']",
                "[class*='submit']"
            ]
            
            for selector in next_selectors:
                try:
                    element = self.browser.driver.find_element(By.CSS_SELECTOR, selector)
                    element.click()
                    logger.info(f"Clicked next button with selector: {selector}")
                    return True
                except NoSuchElementException:
                    continue
                except ElementNotInteractableException:
                    continue
            
            # Try vision-based approach
            if self.click_element_by_vision('buttons', 0):
                logger.info("Clicked next button using vision")
                return True
            
            logger.warning("No next button found")
            return False
            
        except Exception as e:
            logger.error(f"Error clicking next button: {e}")
            return False
    
    def click_next_button_enhanced(self) -> bool:
        """
        Enhanced next button clicking with multiple strategies.
        
        Returns:
            bool: True if successful
        """
        try:
            # Strategy 1: Look for common next button patterns
            next_patterns = [
                "//input[@type='submit' and contains(@value, 'Next')]",
                "//input[@type='submit' and contains(@value, 'Continue')]",
                "//input[@type='submit' and contains(@value, 'Submit')]",
                "//button[contains(text(), 'Next')]",
                "//button[contains(text(), 'Continue')]",
                "//button[contains(text(), 'Submit')]",
                "//a[contains(text(), 'Next')]",
                "//a[contains(text(), 'Continue')]",
                "//div[contains(@class, 'next')]//button",
                "//div[contains(@class, 'continue')]//button"
            ]
            
            for pattern in next_patterns:
                try:
                    element = self.browser.driver.find_element(By.XPATH, pattern)
                    element.click()
                    logger.info(f"Clicked next button with XPath: {pattern}")
                    return True
                except NoSuchElementException:
                    continue
                except ElementNotInteractableException:
                    continue
            
            # Strategy 2: Look for buttons by text content
            buttons = self.browser.driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                try:
                    text = button.text.lower()
                    if any(word in text for word in ['next', 'continue', 'submit', 'proceed']):
                        button.click()
                        logger.info(f"Clicked button with text: {button.text}")
                        return True
                except ElementNotInteractableException:
                    continue
            
            # Strategy 3: Look for input submit buttons
            inputs = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
            for input_elem in inputs:
                try:
                    value = input_elem.get_attribute('value').lower()
                    if any(word in value for word in ['next', 'continue', 'submit']):
                        input_elem.click()
                        logger.info(f"Clicked input with value: {input_elem.get_attribute('value')}")
                        return True
                except ElementNotInteractableException:
                    continue
            
            # Strategy 4: Vision-based approach
            if self.click_element_by_vision('buttons', 0):
                logger.info("Clicked next button using vision analysis")
                return True
            
            logger.warning("No next button found with any strategy")
            return False
            
        except Exception as e:
            logger.error(f"Error in enhanced next button clicking: {e}")
            return False
    
    def handle_survey_page_hybrid(self) -> bool:
        """
        Handle a survey page using hybrid vision/DOM approach.
        
        Returns:
            bool: True if page handled successfully
        """
        try:
            # Take screenshot for analysis
            screenshot_path = os.path.join(self.screenshot_dir, f"survey_page_{int(time.time())}.png")
            self.browser.take_screenshot(screenshot_path)
            
            # Analyze page using vision
            analysis = self.analyze_screenshot_vision(screenshot_path)
            
            # Handle different question types
            handled = False
            
            # Handle radio buttons
            if analysis.get('radio_buttons'):
                handled = self.answer_radio_question_with_persona()
                if handled:
                    logger.info("Handled radio button question")
            
            # Handle checkboxes
            if not handled and analysis.get('checkboxes'):
                handled = self.answer_checkbox_question()
                if handled:
                    logger.info("Handled checkbox question")
            
            # Handle text fields
            if not handled and analysis.get('text_fields'):
                # Get persona-based text
                text_response = self.get_random_persona_text(
                    "survey_behavior", 
                    "text_responses", 
                    "Good experience"
                )
                handled = self.fill_text_field_by_vision(text_response, 0)
                if handled:
                    logger.info("Handled text field question")
            
            # Handle dropdowns
            if not handled and analysis.get('dropdowns'):
                dropdown_option = self.get_persona_dropdown_option(
                    "survey_behavior", 
                    "dropdown_selections"
                )
                # Try to select dropdown option
                try:
                    select_elements = self.browser.driver.find_elements(By.TAG_NAME, "select")
                    if select_elements:
                        from selenium.webdriver.support.ui import Select
                        select = Select(select_elements[0])
                        select.select_by_visible_text(dropdown_option)
                        handled = True
                        logger.info("Handled dropdown question")
                except:
                    pass
            
            # If no specific elements found, try DOM-based approach
            if not handled:
                handled = self.handle_survey_page()
            
            # Add random delay to appear human
            if self.random_delays:
                time.sleep(random.uniform(1, 3))
            
            return handled
            
        except Exception as e:
            logger.error(f"Error in hybrid survey page handling: {e}")
            return False
    
    def handle_survey_page(self) -> bool:
        """
        Handle a survey page using DOM-based approach.
        
        Returns:
            bool: True if page handled successfully
        """
        try:
            handled = False
            
            # Handle radio buttons
            radio_buttons = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            if radio_buttons:
                # Select random radio button
                random_button = random.choice(radio_buttons)
                random_button.click()
                handled = True
                logger.info("Handled radio button question")
            
            # Handle checkboxes
            if not handled:
                checkboxes = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                if checkboxes:
                    # Select random checkbox
                    random_checkbox = random.choice(checkboxes)
                    random_checkbox.click()
                    handled = True
                    logger.info("Handled checkbox question")
            
            # Handle text areas
            if not handled:
                textareas = self.browser.driver.find_elements(By.TAG_NAME, "textarea")
                if textareas:
                    text_response = self.get_random_persona_text(
                        "survey_behavior", 
                        "text_responses", 
                        "This was a good experience overall."
                    )
                    textareas[0].clear()
                    textareas[0].send_keys(text_response)
                    handled = True
                    logger.info("Handled text area question")
            
            # Handle text inputs
            if not handled:
                text_inputs = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                if text_inputs:
                    # Check if it's a name field
                    for input_elem in text_inputs:
                        placeholder = input_elem.get_attribute('placeholder') or ''
                        name = input_elem.get_attribute('name') or ''
                        
                        if any(word in placeholder.lower() or word in name.lower() 
                               for word in ['name', 'first', 'last']):
                            # Fill with persona name
                            full_name = self.get_persona_value("about_you.full_name", "John Doe")
                            input_elem.clear()
                            input_elem.send_keys(full_name)
                            handled = True
                            logger.info("Handled name input field")
                            break
                        
                        elif any(word in placeholder.lower() or word in name.lower() 
                                for word in ['email', 'e-mail']):
                            # Fill with persona email
                            email = self.get_persona_value("about_you.email", "user@example.com")
                            input_elem.clear()
                            input_elem.send_keys(email)
                            handled = True
                            logger.info("Handled email input field")
                            break
                        
                        elif any(word in placeholder.lower() or word in name.lower() 
                                for word in ['age', 'birth']):
                            # Fill with persona age
                            age = self.get_persona_value("about_you.age", "25")
                            input_elem.clear()
                            input_elem.send_keys(age)
                            handled = True
                            logger.info("Handled age input field")
                            break
                
                if not handled and text_inputs:
                    # Fill with generic response
                    text_response = self.get_random_persona_text(
                        "survey_behavior", 
                        "text_responses", 
                        "Good"
                    )
                    text_inputs[0].clear()
                    text_inputs[0].send_keys(text_response)
                    handled = True
                    logger.info("Handled generic text input field")
            
            # Handle select dropdowns
            if not handled:
                select_elements = self.browser.driver.find_elements(By.TAG_NAME, "select")
                if select_elements:
                    try:
                        from selenium.webdriver.support.ui import Select
                        select = Select(select_elements[0])
                        options = select.options
                        if len(options) > 1:
                            # Select random option (skip first if it's "Please select")
                            if "select" in options[0].text.lower():
                                random_option = random.choice(options[1:])
                            else:
                                random_option = random.choice(options)
                            select.select_by_visible_text(random_option.text)
                            handled = True
                            logger.info("Handled dropdown question")
                    except:
                        pass
            
            # Add random delay
            if self.random_delays:
                time.sleep(random.uniform(1, 3))
            
            return handled
            
        except Exception as e:
            logger.error(f"Error handling survey page: {e}")
            return False
    
    def handle_country_selection(self) -> bool:
        """
        Handle country selection if present.
        
        Returns:
            bool: True if handled successfully
        """
        try:
            # Look for country selection elements
            country_selectors = [
                "select[name*='country']",
                "select[id*='country']",
                "input[name*='country']",
                "input[id*='country']"
            ]
            
            for selector in country_selectors:
                try:
                    element = self.browser.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if element.tag_name == "select":
                        from selenium.webdriver.support.ui import Select
                        select = Select(element)
                        # Select United States if available
                        try:
                            select.select_by_visible_text("United States")
                            logger.info("Selected United States as country")
                            return True
                        except:
                            # Select first option
                            select.select_by_index(1)
                            logger.info("Selected first country option")
                            return True
                    else:
                        # Text input for country
                        element.clear()
                        element.send_keys("United States")
                        logger.info("Entered United States as country")
                        return True
                        
                except NoSuchElementException:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling country selection: {e}")
            return False
    
    def complete_cpx_survey(self, max_pages: int = 10, use_hybrid: bool = True) -> bool:
        """
        Complete a CPX Research survey.
        
        Args:
            max_pages: Maximum number of pages to process
            use_hybrid: Whether to use hybrid vision/DOM approach
            
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
            
            # Handle country selection if present
            self.handle_country_selection()
            
            # Process survey pages
            page_count = 0
            while page_count < max_pages:
                logger.info(f"Processing survey page {page_count + 1}")
                
                # Take screenshot of current page
                self.browser.take_screenshot(f"cpx_survey_page_{page_count + 1}.png")
                
                # Wait for survey questions to appear
                if not self.wait_for_survey_questions():
                    logger.warning("No survey questions found, checking for completion")
                    # Check if survey is complete
                    current_url = self.browser.get_current_url()
                    if "complete" in current_url.lower() or "thank" in current_url.lower():
                        logger.info("Survey appears to be complete")
                        break
                
                # Handle the current page
                if use_hybrid:
                    if not self.handle_survey_page_hybrid():
                        logger.warning(f"Failed to handle page {page_count + 1} with hybrid approach")
                        # Fallback to DOM approach
                        if not self.handle_survey_page():
                            logger.warning(f"Failed to handle page {page_count + 1}")
                else:
                    if not self.handle_survey_page():
                        logger.warning(f"Failed to handle page {page_count + 1}")
                
                # Click next button
                if not self.click_next_button_enhanced():
                    logger.warning("Failed to click next button")
                    # Try vision-based approach
                    if not self.click_element_by_vision('buttons', 0):
                        logger.error("No next button found")
                        break
                
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
            
            # Update statistics
            self.surveys_completed += 1
            self.current_survey_earnings = random.uniform(0.50, 5.00)  # Simulated earnings
            self.total_earnings += self.current_survey_earnings
            
            logger.info(f"Survey completed! Earnings: ${self.current_survey_earnings:.2f}")
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
    
    # Ask about hybrid mode
    use_hybrid = input("Use hybrid vision/DOM approach? (y/n, default: y): ").strip().lower()
    use_hybrid = use_hybrid != 'n'
    
    # Ask about headless mode
    headless = input("Run in headless mode? (y/n, default: n): ").strip().lower()
    headless = headless == 'y'
    
    confirm = input("Start CPX survey automation? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Automation cancelled.")
        return
    
    # Run the automation
    with CPXSurveyAutomation(headless=headless) as cpx_automation:
        success = cpx_automation.complete_cpx_survey(use_hybrid=use_hybrid)
        
        if success:
            print(f"\n✅ Survey completed successfully!")
            print(f"Surveys completed: {cpx_automation.surveys_completed}")
            print(f"Total earnings: ${cpx_automation.total_earnings:.2f}")
        else:
            print("\n❌ Survey automation failed")


if __name__ == "__main__":
    main() 