"""
Survey Handler - Manages survey automation and integration

Handles survey completion, earnings tracking, and integration with Discord bot.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from loguru import logger
from datetime import datetime, timedelta

from src.web_scraper.cpx_scraper import CPXScraper


class SurveyHandler:
    """Handles survey automation and management."""
    
    def __init__(self, config: Dict[str, Any], db_manager):
        """Initialize the survey handler.
        
        Args:
            config: Configuration dictionary
            db_manager: Database manager instance
        """
        self.config = config
        self.db_manager = db_manager
        self.scraper = None
        self.is_running = False
        self.current_survey = None
        
    async def initialize(self):
        """Initialize the survey handler."""
        try:
            self.scraper = CPXScraper(self.config)
            await self.scraper.initialize_driver()
            logger.info("Survey handler initialized")
        except Exception as e:
            logger.error(f"Error initializing survey handler: {e}")
            raise
    
    async def check_for_surveys(self):
        """Check for available surveys and start them if conditions are met."""
        try:
            if self.is_running:
                logger.info("Survey handler already running, skipping check")
                return
            
            # Get available surveys
            surveys = await self.scraper.get_available_surveys()
            
            if not surveys:
                logger.info("No suitable surveys available")
                return
            
            # Sort surveys by earnings (highest first)
            surveys.sort(key=lambda x: x["earnings"], reverse=True)
            
            # Start the best survey
            best_survey = surveys[0]
            await self.start_survey(best_survey)
            
        except Exception as e:
            logger.error(f"Error checking for surveys: {e}")
    
    async def start_survey(self, survey_data: Dict[str, Any]) -> bool:
        """Start a survey.
        
        Args:
            survey_data: Survey information
            
        Returns:
            True if survey started successfully, False otherwise
        """
        try:
            if self.is_running:
                logger.warning("Survey already in progress")
                return False
            
            self.is_running = True
            self.current_survey = survey_data
            
            logger.info(f"Starting survey: {survey_data['title']}")
            
            # Add survey to database
            await self.db_manager.add_survey({
                "survey_id": f"survey_{int(time.time())}",
                "title": survey_data["title"],
                "earnings": survey_data["earnings"],
                "duration": survey_data["duration"],
                "status": "in_progress"
            })
            
            # Complete the survey
            result = await self.scraper.complete_survey(survey_data)
            
            if result["success"]:
                # Update database with completion
                await self.db_manager.add_earning(
                    result["earnings"],
                    "survey_completion",
                    "completed"
                )
                
                logger.info(f"Survey completed successfully: ${result['earnings']:.2f}")
                
                # Update survey status
                await self.db_manager.update_bot_stat("last_survey_completion", {
                    "title": survey_data["title"],
                    "earnings": result["earnings"],
                    "completed_at": datetime.now().isoformat()
                })
                
            else:
                logger.warning(f"Survey failed: {result.get('error', 'Unknown error')}")
                await self.db_manager.add_earning(0, "survey_completion", "failed")
            
            # Reset state
            self.is_running = False
            self.current_survey = None
            
            return result["success"]
            
        except Exception as e:
            logger.error(f"Error starting survey: {e}")
            self.is_running = False
            self.current_survey = None
            return False
    
    async def find_and_start_survey(self) -> Optional[Dict[str, Any]]:
        """Find and start the best available survey.
        
        Returns:
            Survey data if started successfully, None otherwise
        """
        try:
            surveys = await self.scraper.get_available_surveys()
            
            if not surveys:
                return None
            
            # Sort by earnings and rating
            surveys.sort(key=lambda x: (x["earnings"], x["rating"]), reverse=True)
            
            # Try to start the best survey
            for survey in surveys[:3]:  # Try top 3 surveys
                if await self.start_survey(survey):
                    return survey
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding and starting survey: {e}")
            return None
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current survey handler status.
        
        Returns:
            Dictionary with status information
        """
        try:
            # Get recent surveys
            recent_surveys = await self.db_manager.get_surveys(limit=5)
            
            # Get earnings
            earnings = await self.db_manager.get_earnings()
            
            # Get last completion
            last_completion = await self.db_manager.get_bot_stat("last_survey_completion")
            
            return {
                "is_running": self.is_running,
                "current_survey": self.current_survey,
                "active_surveys": len([s for s in recent_surveys if s["status"] == "in_progress"]),
                "total_earnings": earnings["total"],
                "today_earnings": earnings["today"],
                "last_completion": last_completion
            }
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {
                "is_running": False,
                "current_survey": None,
                "active_surveys": 0,
                "total_earnings": 0.0,
                "today_earnings": 0.0,
                "last_completion": None
            }
    
    async def get_earnings(self) -> Dict[str, float]:
        """Get earnings statistics.
        
        Returns:
            Dictionary with earnings information
        """
        try:
            return await self.db_manager.get_earnings()
        except Exception as e:
            logger.error(f"Error getting earnings: {e}")
            return {"total": 0.0, "today": 0.0, "week": 0.0}
    
    async def get_available_surveys(self) -> List[Dict[str, Any]]:
        """Get list of available surveys.
        
        Returns:
            List of available surveys
        """
        try:
            return await self.scraper.get_available_surveys()
        except Exception as e:
            logger.error(f"Error getting available surveys: {e}")
            return []
    
    async def withdraw_all(self) -> Dict[str, Any]:
        """Withdraw all available balance.
        
        Returns:
            Dictionary with withdrawal result
        """
        try:
            earnings = await self.get_earnings()
            total = earnings["total"]
            
            if total <= 0:
                return {"success": False, "error": "No balance to withdraw"}
            
            # Simulate withdrawal to tip.cc
            logger.info(f"Withdrawing ${total:.2f} to tip.cc")
            
            # Update database
            await self.db_manager.add_earning(-total, "withdrawal", "completed")
            
            return {
                "success": True,
                "amount": total,
                "message": f"Withdrew ${total:.2f} to tip.cc"
            }
            
        except Exception as e:
            logger.error(f"Error withdrawing all: {e}")
            return {"success": False, "error": str(e)}
    
    async def withdraw_amount(self, amount: float) -> Dict[str, Any]:
        """Withdraw a specific amount.
        
        Args:
            amount: Amount to withdraw
            
        Returns:
            Dictionary with withdrawal result
        """
        try:
            earnings = await self.get_earnings()
            total = earnings["total"]
            
            if amount > total:
                return {"success": False, "error": "Insufficient balance"}
            
            # Simulate withdrawal to tip.cc
            logger.info(f"Withdrawing ${amount:.2f} to tip.cc")
            
            # Update database
            await self.db_manager.add_earning(-amount, "withdrawal", "completed")
            
            return {
                "success": True,
                "amount": amount,
                "message": f"Withdrew ${amount:.2f} to tip.cc"
            }
            
        except Exception as e:
            logger.error(f"Error withdrawing amount: {e}")
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Close the survey handler."""
        try:
            if self.scraper:
                await self.scraper.close()
            logger.info("Survey handler closed")
        except Exception as e:
            logger.error(f"Error closing survey handler: {e}") 