#!/usr/bin/env python3
"""
Survey Automation Script

This script demonstrates how to use Firefox automation for survey completion.
"""

import time
import random
import json
import os
from selenium.webdriver.common.by import By
from loguru import logger
from src.web_automation.firefox_automation import FirefoxAutomation
from src.web_automation.survey_automator import SurveyAutomator


def demo_survey_automation():
    """
    Demonstrate Firefox automation for survey completion.
    """
    # Initialize Firefox automation (not headless so you can see the browser)
    with FirefoxAutomation(headless=False) as browser:
        
        # Example 1: Navigate to a survey website
        logger.info("Starting survey automation demo...")
        
        # Navigate to a sample survey site (replace with actual survey URL)
        survey_url = "https://www.example-survey-site.com"
        
        if browser.navigate_to_url(survey_url):
            logger.info(f"Successfully navigated to: {survey_url}")
            logger.info(f"Page title: {browser.get_page_title()}")
            
            # Wait a moment to see the page
            time.sleep(3)
            
            # Example survey interactions (adjust selectors based on actual survey)
            
            # 1. Fill out a name field
            browser.fill_input(By.ID, "name", "John Doe")
            
            # 2. Fill out an email field
            browser.fill_input(By.ID, "email", "john.doe@example.com")
            
            # 3. Select age range from dropdown
            browser.select_option(By.ID, "age-range", "25-34")
            
            # 4. Click a radio button for gender
            browser.click_element(By.ID, "gender-male")
            
            # 5. Check a checkbox for interests
            browser.click_element(By.ID, "interest-technology")
            
            # 6. Fill out a text area
            browser.fill_input(By.ID, "feedback", "This is a great survey platform!")
            
            # 7. Submit the form
            browser.click_element(By.ID, "submit-button")
            
            # Wait for submission
            time.sleep(2)
            
            # Take a screenshot of the result
            browser.take_screenshot("survey_completion.png")
            
            logger.info("Survey automation demo completed!")
            
        else:
            logger.error("Failed to navigate to survey URL")


def advanced_survey_automation():
    """
    Use the advanced SurveyAutomator to complete surveys from configuration.
    """
    config_file = "config/survey_config.json"
    
    if not os.path.exists(config_file):
        logger.error(f"Configuration file not found: {config_file}")
        return
    
    # Load survey configuration
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    with SurveyAutomator(headless=False) as automator:
        for survey in config["surveys"]:
            logger.info(f"Starting survey: {survey['name']}")
            
            # Complete the survey
            if automator.complete_survey(survey):
                logger.info(f"Successfully completed survey: {survey['name']}")
                
                # Take screenshot if enabled
                if config["settings"].get("screenshot_on_completion", False):
                    automator.browser.take_screenshot(f"survey_{survey['name'].lower().replace(' ', '_')}.png")
            else:
                logger.error(f"Failed to complete survey: {survey['name']}")
            
            # Wait between surveys
            time.sleep(5)


def interactive_survey_mode():
    """
    Interactive mode where you can manually control the browser.
    """
    with FirefoxAutomation(headless=False) as browser:
        
        # Navigate to a survey site
        survey_url = input("Enter survey URL: ").strip()
        
        if not survey_url:
            survey_url = "https://www.google.com"  # Default fallback
        
        if browser.navigate_to_url(survey_url):
            logger.info(f"Browser opened and navigated to: {survey_url}")
            logger.info("You can now manually interact with the browser.")
            logger.info("Press Ctrl+C to close the browser when done.")
            
            try:
                # Keep the browser open for manual interaction
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Closing browser...")
        else:
            logger.error("Failed to navigate to the specified URL")


def create_survey_config():
    """
    Interactive survey configuration creator.
    """
    print("Survey Configuration Creator")
    print("=" * 30)
    
    survey_name = input("Enter survey name: ").strip()
    survey_url = input("Enter survey URL: ").strip()
    
    if not survey_name or not survey_url:
        print("Survey name and URL are required!")
        return
    
    # Create basic survey configuration
    survey_config = {
        "name": survey_name,
        "url": survey_url,
        "description": input("Enter survey description (optional): ").strip() or "",
        "questions": []
    }
    
    # Add login if needed
    has_login = input("Does this survey require login? (y/n): ").lower().strip() == 'y'
    if has_login:
        survey_config["login"] = {
            "username_field": input("Username field selector: ").strip(),
            "password_field": input("Password field selector: ").strip(),
            "username": input("Username: ").strip(),
            "password": input("Password: ").strip(),
            "submit_button": input("Login button selector: ").strip()
        }
    
    # Add questions
    print("\nAdding questions (press Enter when done):")
    question_num = 1
    
    while True:
        print(f"\nQuestion {question_num}:")
        question_type = input("Question type (text/multiple_choice/scale/dropdown): ").strip().lower()
        
        if not question_type:
            break
        
        if question_type not in ["text", "multiple_choice", "scale", "dropdown"]:
            print("Invalid question type!")
            continue
        
        question = {
            "type": question_type,
            "selector": input("Element selector: ").strip(),
            "description": input("Question description: ").strip()
        }
        
        if question_type == "text":
            question["answer"] = input("Answer text: ").strip()
        elif question_type == "multiple_choice":
            question["answer_index"] = int(input("Answer index (0-based): ").strip())
        elif question_type == "scale":
            question["rating"] = int(input("Rating (1-10): ").strip())
        elif question_type == "dropdown":
            question["option"] = input("Option text: ").strip()
        
        survey_config["questions"].append(question)
        question_num += 1
    
    # Add submit button
    submit_button = input("Submit button selector: ").strip()
    if submit_button:
        survey_config["submit_button"] = submit_button
    
    # Save configuration
    config_file = f"config/{survey_name.lower().replace(' ', '_')}_config.json"
    os.makedirs("config", exist_ok=True)
    
    with open(config_file, 'w') as f:
        json.dump({"surveys": [survey_config]}, f, indent=2)
    
    print(f"\nSurvey configuration saved to: {config_file}")


def main():
    """
    Main function to run survey automation.
    """
    print("Firefox Survey Automation")
    print("=" * 30)
    print("1. Demo Survey Automation")
    print("2. Advanced Survey Automation (from config)")
    print("3. Interactive Mode")
    print("4. Create Survey Configuration")
    print("5. Exit")
    
    choice = input("\nSelect an option (1-5): ").strip()
    
    if choice == "1":
        demo_survey_automation()
    elif choice == "2":
        advanced_survey_automation()
    elif choice == "3":
        interactive_survey_mode()
    elif choice == "4":
        create_survey_config()
    elif choice == "5":
        print("Goodbye!")
    else:
        print("Invalid choice. Please select 1-5.")


if __name__ == "__main__":
    main() 