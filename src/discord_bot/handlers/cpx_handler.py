"""
CPX Research Handler - Discord Bot Integration

Handles CPX Research survey automation for Discord bot integration.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from loguru import logger
from datetime import datetime, timedelta

from ...web_scraper.cpx_scraper import CPXScraper


class CPXHandler:
    """Handler for CPX Research survey automation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the CPX handler.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.cpx_config = config.get("cpx_research", {})
        self.scraper = None
        self.is_running = False
        self.current_session = None
        
    async def initialize(self):
        """Initialize the CPX scraper."""
        try:
            self.scraper = CPXScraper(self.config)
            await self.scraper.initialize_driver()
            logger.info("CPX Handler initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing CPX Handler: {e}")
            raise
    
    async def run_survey_automation(self) -> Dict[str, Any]:
        """Run CPX Research survey automation.
        
        Returns:
            Dictionary with automation results
        """
        if self.is_running:
            logger.warning("CPX automation already running")
            return {"error": "Automation already running"}
        
        self.is_running = True
        start_time = datetime.now()
        surveys_completed = 0
        total_earnings = 0.0
        
        try:
            # Initialize scraper if not already done
            if not self.scraper:
                await self.initialize()
            
            # Get available surveys
            surveys = await self.scraper.get_available_surveys()
            
            if not surveys:
                logger.info("No surveys available")
                return {
                    "surveys_completed": 0,
                    "total_earnings": 0.0,
                    "duration_minutes": 0,
                    "status": "no_surveys_available"
                }
            
            logger.info(f"Found {len(surveys)} available surveys")
            
            # Process each survey
            for survey in surveys:
                if not self.is_running:
                    break
                
                try:
                    # Check if survey meets criteria
                    if not self._meets_criteria(survey):
                        continue
                    
                    # Start and complete survey
                    success = await self.scraper.start_survey(survey)
                    if success:
                        result = await self.scraper.complete_survey(survey)
                        
                        if result.get("completed"):
                            surveys_completed += 1
                            total_earnings += result.get("earnings", 0.0)
                            
                            logger.info(f"Completed survey: {survey.get('title', 'Unknown')} - ${result.get('earnings', 0.0)}")
                            
                            # Add delay between surveys
                            await asyncio.sleep(random.randint(30, 120))
                    
                except Exception as e:
                    logger.error(f"Error processing survey {survey.get('id', 'Unknown')}: {e}")
                    continue
            
            # Calculate session duration
            duration = datetime.now() - start_time
            duration_minutes = duration.total_seconds() / 60
            
            return {
                "surveys_completed": surveys_completed,
                "total_earnings": total_earnings,
                "duration_minutes": round(duration_minutes, 2),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error in CPX automation: {e}")
            return {
                "surveys_completed": surveys_completed,
                "total_earnings": total_earnings,
                "duration_minutes": 0,
                "status": "error",
                "error": str(e)
            }
        finally:
            self.is_running = False
            if self.scraper:
                await self.scraper.close()
    
    def _meets_criteria(self, survey: Dict[str, Any]) -> bool:
        """Check if survey meets acceptance criteria."""
        try:
            survey_settings = self.cpx_config.get("survey_settings", {})
            
            # Check minimum earnings
            min_earnings = survey_settings.get("min_earnings", 0.0)
            survey_earnings = survey.get("earnings", 0.0)
            if survey_earnings < min_earnings:
                return False
            
            # Check maximum time
            max_time = survey_settings.get("max_time", 30)
            survey_time = survey.get("estimated_time", 0)
            if survey_time > max_time:
                return False
            
            # Check survey types
            target_types = survey_settings.get("survey_types", [])
            survey_type = survey.get("type", "").lower()
            if target_types and survey_type not in target_types:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking survey criteria: {e}")
            return False
    
    async def get_available_surveys(self) -> List[Dict[str, Any]]:
        """Get list of available surveys."""
        try:
            if not self.scraper:
                await self.initialize()
            
            surveys = await self.scraper.get_available_surveys()
            return surveys
            
        except Exception as e:
            logger.error(f"Error getting available surveys: {e}")
            return []
    
    async def get_user_balance(self, user_id: str) -> float:
        """Get user's current balance."""
        try:
            # This would typically query the Discord bot's database
            # For now, return a placeholder value
            return 25.50
        except Exception as e:
            logger.error(f"Error getting user balance: {e}")
            return 0.0
    
    async def process_withdrawal(self, user_id: str, amount: float) -> Dict[str, Any]:
        """Process withdrawal request."""
        try:
            current_balance = await self.get_user_balance(user_id)
            
            if amount > current_balance:
                return {
                    "success": False,
                    "error": "Insufficient balance",
                    "current_balance": current_balance
                }
            
            # This would typically update the database and process the withdrawal
            # For now, return success
            return {
                "success": True,
                "amount": amount,
                "new_balance": current_balance - amount
            }
            
        except Exception as e:
            logger.error(f"Error processing withdrawal: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop_automation(self):
        """Stop the current automation session."""
        self.is_running = False
        if self.scraper:
            await self.scraper.close()
        logger.info("CPX automation stopped")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current CPX handler status."""
        return {
            "is_running": self.is_running,
            "scraper_initialized": self.scraper is not None,
            "current_session": self.current_session
        }


# Import random for delays
import random 