#!/usr/bin/env python3
"""
CPX Research Automation Demo

This script demonstrates how to use the CPX Research survey automation.
"""

import time
from loguru import logger
from cpx_survey_automation import CPXSurveyAutomation


def demo_cpx_automation():
    """
    Demonstrate CPX Research survey automation.
    """
    print("CPX Research Survey Automation Demo")
    print("=" * 40)
    print("This demo will:")
    print("1. Open Firefox browser")
    print("2. Navigate to CPX Research")
    print("3. Automatically answer survey questions")
    print("4. Take screenshots of each page")
    print("5. Complete the survey")
    print()
    
    # Configure CPX credentials
    user_id = "533055960609193994"  # From your URL
    app_id = "27260"  # From your URL
    
    print(f"Using CPX Research URL: https://offers.cpx-research.com/index.php")
    print(f"User ID: {user_id}")
    print(f"App ID: {app_id}")
    print()
    
    # Run the automation
    with CPXSurveyAutomation(headless=False) as cpx_automation:
        # Update credentials
        cpx_automation.user_id = user_id
        cpx_automation.app_id = app_id
        
        logger.info("Starting CPX Research survey automation...")
        
        # Complete the survey
        success = cpx_automation.complete_cpx_survey(max_pages=5)
        
        if success:
            logger.info("✅ CPX survey automation completed successfully!")
            print("\n✅ Survey automation completed!")
            print("Check the screenshots in the current directory:")
            print("- cpx_survey_page_1.png")
            print("- cpx_survey_page_2.png")
            print("- ...")
            print("- cpx_survey_complete.png")
        else:
            logger.error("❌ CPX survey automation failed")
            print("\n❌ Survey automation failed. Check the logs for details.")


def interactive_cpx_mode():
    """
    Interactive mode for CPX Research automation.
    """
    print("CPX Research Interactive Mode")
    print("=" * 30)
    print("This mode will open Firefox and navigate to CPX Research.")
    print("You can then manually control the browser or let it auto-answer.")
    print()
    
    user_id = input("Enter your CPX user ID: ").strip()
    app_id = input("Enter your CPX app ID: ").strip()
    
    if not user_id or not app_id:
        print("User ID and App ID are required!")
        return
    
    with CPXSurveyAutomation(headless=False) as cpx_automation:
        cpx_automation.user_id = user_id
        cpx_automation.app_id = app_id
        
        # Navigate to CPX Research
        if cpx_automation.navigate_to_cpx():
            print(f"✅ Successfully navigated to CPX Research")
            print(f"Current URL: {cpx_automation.browser.get_current_url()}")
            print(f"Page title: {cpx_automation.browser.get_page_title()}")
            print()
            print("Firefox browser is now open with CPX Research.")
            print("You can manually interact with the survey or press Ctrl+C to close.")
            
            try:
                # Keep browser open for manual interaction
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nClosing browser...")
        else:
            print("❌ Failed to navigate to CPX Research")


def main():
    """
    Main function to run CPX automation demo.
    """
    print("CPX Research Automation Demo")
    print("=" * 30)
    print("1. Full Automation Demo")
    print("2. Interactive Mode")
    print("3. Exit")
    
    choice = input("\nSelect an option (1-3): ").strip()
    
    if choice == "1":
        demo_cpx_automation()
    elif choice == "2":
        interactive_cpx_mode()
    elif choice == "3":
        print("Goodbye!")
    else:
        print("Invalid choice. Please select 1-3.")


if __name__ == "__main__":
    main() 