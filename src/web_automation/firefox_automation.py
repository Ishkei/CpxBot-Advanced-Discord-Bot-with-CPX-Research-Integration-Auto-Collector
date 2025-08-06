"""
Firefox Automation Module

This module provides Firefox browser automation capabilities for survey completion.
"""

import time
import random
from typing import Optional, List, Dict, Any
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.firefox import GeckoDriverManager
from loguru import logger


class FirefoxAutomation:
    """
    Firefox browser automation class for survey completion.
    """
    
    def __init__(self, headless: bool = False, user_agent: Optional[str] = None):
        """
        Initialize Firefox automation.
        
        Args:
            headless: Whether to run Firefox in headless mode
            user_agent: Custom user agent string
        """
        self.driver = None
        self.headless = headless
        self.user_agent = user_agent or self._get_default_user_agent()
        self.wait_timeout = 10
        
    def _get_default_user_agent(self) -> str:
        """Get a realistic user agent string."""
        return "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
    
    def start_browser(self) -> bool:
        """
        Start Firefox browser with appropriate options.
        
        Returns:
            bool: True if browser started successfully, False otherwise
        """
        try:
            # Configure Firefox options
            options = Options()
            
            if self.headless:
                options.add_argument("--headless")
            
            # Set user agent
            options.set_preference("general.useragent.override", self.user_agent)
            
            # Disable images for faster loading (optional)
            options.set_preference("permissions.default.image", 2)
            
            # Disable notifications
            options.set_preference("dom.webnotifications.enabled", False)
            
            # Disable geolocation
            options.set_preference("geo.enabled", False)
            
            # Set window size
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            
            # Initialize the driver
            service = Service(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=options)
            
            # Set implicit wait
            self.driver.implicitly_wait(5)
            
            logger.info("Firefox browser started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Firefox browser: {e}")
            return False
    
    def navigate_to_url(self, url: str) -> bool:
        """
        Navigate to a specific URL.
        
        Args:
            url: The URL to navigate to
            
        Returns:
            bool: True if navigation successful, False otherwise
        """
        try:
            if not self.driver:
                logger.error("Browser not started. Call start_browser() first.")
                return False
            
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            logger.info("Page loaded successfully")
            return True
            
        except TimeoutException:
            logger.error(f"Timeout waiting for page to load: {url}")
            return False
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    def find_element_safe(self, by: By, value: str, timeout: int = None) -> Optional[Any]:
        """
        Safely find an element with timeout.
        
        Args:
            by: Selenium By strategy
            value: Element identifier
            timeout: Timeout in seconds (uses default if None)
            
        Returns:
            Element if found, None otherwise
        """
        try:
            timeout = timeout or self.wait_timeout
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.warning(f"Element not found: {by}={value}")
            return None
    
    def click_element(self, by: By, value: str) -> bool:
        """
        Click on an element safely.
        
        Args:
            by: Selenium By strategy
            value: Element identifier
            
        Returns:
            bool: True if click successful, False otherwise
        """
        try:
            element = self.find_element_safe(by, value)
            if element:
                element.click()
                logger.info(f"Clicked element: {by}={value}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to click element {by}={value}: {e}")
            return False
    
    def fill_input(self, by: By, value: str, text: str) -> bool:
        """
        Fill an input field with text.
        
        Args:
            by: Selenium By strategy
            value: Element identifier
            text: Text to enter
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            element = self.find_element_safe(by, value)
            if element:
                element.clear()
                element.send_keys(text)
                logger.info(f"Filled input {by}={value} with: {text}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to fill input {by}={value}: {e}")
            return False
    
    def select_option(self, by: By, value: str, option_text: str) -> bool:
        """
        Select an option from a dropdown.
        
        Args:
            by: Selenium By strategy
            value: Element identifier
            option_text: Text of the option to select
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from selenium.webdriver.support.ui import Select
            element = self.find_element_safe(by, value)
            if element:
                select = Select(element)
                select.select_by_visible_text(option_text)
                logger.info(f"Selected option '{option_text}' from {by}={value}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to select option '{option_text}' from {by}={value}: {e}")
            return False
    
    def wait_for_element(self, by: By, value: str, timeout: int = None) -> bool:
        """
        Wait for an element to be present.
        
        Args:
            by: Selenium By strategy
            value: Element identifier
            timeout: Timeout in seconds
            
        Returns:
            bool: True if element found, False otherwise
        """
        try:
            timeout = timeout or self.wait_timeout
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            logger.warning(f"Element not found within timeout: {by}={value}")
            return False
    
    def get_page_title(self) -> str:
        """Get the current page title."""
        return self.driver.title if self.driver else ""
    
    def get_current_url(self) -> str:
        """Get the current URL."""
        return self.driver.current_url if self.driver else ""
    
    def take_screenshot(self, filename: str = None) -> bool:
        """
        Take a screenshot of the current page.
        
        Args:
            filename: Screenshot filename (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return False
    
    def close_browser(self):
        """Close the Firefox browser."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("Firefox browser closed")
    
    def __enter__(self):
        """Context manager entry."""
        self.start_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_browser() 