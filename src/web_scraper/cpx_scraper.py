"""
CPX Research Web Scraper

Handles web scraping and automation for CPX Research surveys.
"""

import asyncio
import time
import random
from typing import Dict, List, Any, Optional
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests


class CPXScraper:
    """Web scraper for CPX Research surveys."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the CPX scraper.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.driver = None
        self.session = requests.Session()
        self.base_url = config["cpx_research"]["base_url"]
        self.username = config["cpx_research"]["username"]
        self.password = config["cpx_research"]["password"]
        self.survey_settings = config["cpx_research"]["survey_settings"]
        
        # Setup session headers
        self.session.headers.update({
            'User-Agent': config["web_scraper"]["user_agent"],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    async def initialize_driver(self):
        """Initialize the Chrome WebDriver."""
        try:
            chrome_options = Options()
            
            if self.config["web_scraper"]["headless"]:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"--user-agent={self.config['web_scraper']['user_agent']}")
            
            # Add additional options for stealth
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Initialize driver
            self.driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            # Execute stealth script
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Chrome WebDriver initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing WebDriver: {e}")
            raise
    
    async def login(self) -> bool:
        """Login to CPX Research.
        
        Returns:
            True if login successful, False otherwise
        """
        try:
            if not self.driver:
                await self.initialize_driver()
            
            # Navigate to login page
            login_url = f"{self.base_url}/login"
            self.driver.get(login_url)
            
            # Wait for page to load
            await asyncio.sleep(2)
            
            # Find and fill username field
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.clear()
            username_field.send_keys(self.username)
            
            # Find and fill password field
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Submit login form
            submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
            
            # Wait for login to complete
            await asyncio.sleep(3)
            
            # Check if login was successful
            if "dashboard" in self.driver.current_url or "offers" in self.driver.current_url:
                logger.info("Login successful")
                return True
            else:
                logger.error("Login failed")
                return False
                
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False
    
    async def get_available_surveys(self) -> List[Dict[str, Any]]:
        """Get list of available surveys.
        
        Returns:
            List of survey dictionaries
        """
        try:
            if not self.driver:
                await self.login()
            
            # Navigate to offers page
            offers_url = f"{self.base_url}/offers"
            self.driver.get(offers_url)
            
            # Wait for page to load
            await asyncio.sleep(3)
            
            # Parse survey cards
            surveys = []
            survey_cards = self.driver.find_elements(By.CLASS_NAME, "survey-card")
            
            for card in survey_cards:
                try:
                    # Extract survey information
                    earnings_elem = card.find_element(By.CLASS_NAME, "earnings")
                    earnings = float(earnings_elem.text.replace("$", "").strip())
                    
                    time_elem = card.find_element(By.CLASS_NAME, "time")
                    time_text = time_elem.text
                    duration = int(time_text.split()[0])  # Extract minutes
                    
                    rating_elem = card.find_element(By.CLASS_NAME, "rating")
                    rating = float(rating_elem.get_attribute("data-rating") or "0")
                    
                    title_elem = card.find_element(By.CLASS_NAME, "title")
                    title = title_elem.text.strip()
                    
                    # Check if survey meets criteria
                    if (earnings >= self.survey_settings["min_earnings"] and 
                        duration <= self.survey_settings["max_time"]):
                        
                        surveys.append({
                            "title": title,
                            "earnings": earnings,
                            "duration": duration,
                            "rating": rating,
                            "element": card
                        })
                        
                except Exception as e:
                    logger.warning(f"Error parsing survey card: {e}")
                    continue
            
            logger.info(f"Found {len(surveys)} suitable surveys")
            return surveys
            
        except Exception as e:
            logger.error(f"Error getting available surveys: {e}")
            return []
    
    async def start_survey(self, survey_data: Dict[str, Any]) -> bool:
        """Start a specific survey.
        
        Args:
            survey_data: Survey information
            
        Returns:
            True if survey started successfully, False otherwise
        """
        try:
            # Click on the survey card
            survey_data["element"].click()
            
            # Wait for survey to load
            await asyncio.sleep(3)
            
            # Check if survey is available
            if "survey not available" in self.driver.page_source.lower():
                logger.warning("Survey not available")
                return False
            
            logger.info(f"Started survey: {survey_data['title']}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting survey: {e}")
            return False
    
    async def complete_survey(self, survey_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete a survey automatically.
        
        Args:
            survey_data: Survey information
            
        Returns:
            Dictionary with completion results
        """
        try:
            if not await self.start_survey(survey_data):
                return {"success": False, "error": "Failed to start survey"}
            
            # Track survey progress
            progress = 0
            start_time = time.time()
            
            while progress < 100:
                try:
                    # Find current question
                    question_elem = self.driver.find_element(By.CLASS_NAME, "question")
                    question_text = question_elem.text.strip()
                    
                    # Determine question type and answer accordingly
                    await self._answer_question(question_text)
                    
                    # Click continue/next button
                    next_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Continue') or contains(text(), 'Next')]")
                    next_button.click()
                    
                    # Wait for next question
                    await asyncio.sleep(random.uniform(2, 5))
                    
                    # Update progress
                    progress_elem = self.driver.find_element(By.CLASS_NAME, "progress")
                    progress = int(progress_elem.get_attribute("data-progress") or "0")
                    
                    # Check for timeout
                    if time.time() - start_time > survey_data["duration"] * 60:
                        logger.warning("Survey timeout reached")
                        break
                        
                except NoSuchElementException:
                    # Survey might be complete
                    break
                except Exception as e:
                    logger.error(f"Error during survey completion: {e}")
                    break
            
            # Check if survey was completed successfully
            if "thank you" in self.driver.page_source.lower() or "completed" in self.driver.page_source.lower():
                logger.info(f"Survey completed successfully: {survey_data['title']}")
                return {
                    "success": True,
                    "earnings": survey_data["earnings"],
                    "duration": time.time() - start_time
                }
            else:
                logger.warning("Survey may not have been completed properly")
                return {"success": False, "error": "Survey completion uncertain"}
                
        except Exception as e:
            logger.error(f"Error completing survey: {e}")
            return {"success": False, "error": str(e)}
    
    async def _answer_question(self, question_text: str):
        """Answer a survey question based on its type.
        
        Args:
            question_text: The question text
        """
        try:
            # Determine question type and answer accordingly
            if "rate" in question_text.lower() or "scale" in question_text.lower():
                await self._answer_rating_question()
            elif "select" in question_text.lower() or "choose" in question_text.lower():
                await self._answer_choice_question()
            elif "text" in question_text.lower() or "describe" in question_text.lower():
                await self._answer_text_question()
            elif "rank" in question_text.lower():
                await self._answer_ranking_question()
            else:
                # Default to choice question
                await self._answer_choice_question()
                
        except Exception as e:
            logger.error(f"Error answering question: {e}")
    
    async def _answer_rating_question(self):
        """Answer a rating/scale question."""
        try:
            # Find rating options (usually radio buttons or stars)
            rating_options = self.driver.find_elements(By.XPATH, "//input[@type='radio']")
            
            if rating_options:
                # Select a random rating (3-5 for positive responses)
                selected_option = random.choice(rating_options[2:5])
                selected_option.click()
            else:
                # Try star ratings
                stars = self.driver.find_elements(By.CLASS_NAME, "star")
                if stars:
                    # Click on a random star (3-5 stars)
                    selected_star = random.choice(stars[2:5])
                    selected_star.click()
                    
        except Exception as e:
            logger.error(f"Error answering rating question: {e}")
    
    async def _answer_choice_question(self):
        """Answer a multiple choice question."""
        try:
            # Find all choice options
            choices = self.driver.find_elements(By.XPATH, "//input[@type='radio'] | //input[@type='checkbox']")
            
            if choices:
                # Select a random choice
                selected_choice = random.choice(choices)
                selected_choice.click()
                
        except Exception as e:
            logger.error(f"Error answering choice question: {e}")
    
    async def _answer_text_question(self):
        """Answer a text input question."""
        try:
            # Find text input field
            text_input = self.driver.find_element(By.XPATH, "//textarea | //input[@type='text']")
            
            # Generate a generic response
            responses = [
                "This is a good product/service that meets my needs.",
                "I would recommend this to others based on my experience.",
                "The quality and features are satisfactory for the price.",
                "I find this useful and would consider using it again.",
                "Overall, I'm satisfied with this option."
            ]
            
            response = random.choice(responses)
            text_input.clear()
            text_input.send_keys(response)
            
        except Exception as e:
            logger.error(f"Error answering text question: {e}")
    
    async def _answer_ranking_question(self):
        """Answer a ranking question."""
        try:
            # Find draggable items
            items = self.driver.find_elements(By.CLASS_NAME, "draggable")
            ranking_slots = self.driver.find_elements(By.CLASS_NAME, "ranking-slot")
            
            if items and ranking_slots:
                # Drag items to ranking slots in random order
                for i, slot in enumerate(ranking_slots[:3]):  # Top 3 rankings
                    if items:
                        item = random.choice(items)
                        # Simulate drag and drop
                        self.driver.execute_script("arguments[0].appendChild(arguments[1]);", slot, item)
                        items.remove(item)
                        
        except Exception as e:
            logger.error(f"Error answering ranking question: {e}")
    
    async def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("WebDriver closed")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize_driver()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close() 