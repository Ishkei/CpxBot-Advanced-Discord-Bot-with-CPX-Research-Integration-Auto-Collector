"""
CPX Handler - Manages CPX Research Survey Automation

This module is responsible for initializing and running the CPX survey automation.
"""

import asyncio
from loguru import logger
from typing import Dict, Any

from cpx_survey_automation import CPXSurveyAutomation

class CPXHandler:
    """Handles the execution of CPX Research survey automation."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the CPX handler with configuration.

        Args:
            config: Application configuration
        """
        self.config = config.get("cpx_research", {})
        self.user_id = self.config.get("user_id")
        self.app_id = self.config.get("app_id")

    async def run_survey_automation(self) -> Dict[str, Any]:
        """
        Run the CPX survey automation in a separate thread.

        Returns:
            A dictionary with the results of the automation.
        """
        if not self.user_id or not self.app_id:
            logger.error("CPX user_id or app_id not configured.")
            return {"error": "CPX credentials not configured."}

        loop = asyncio.get_event_loop()
        
        try:
            # Run the automation in a separate thread to avoid blocking
            automation_task = loop.run_in_executor(
                None,
                self._run_automation_sync
            )
            
            results = await automation_task
            return results
            
        except Exception as e:
            logger.error(f"Error running CPX survey automation: {e}")
            return {"error": str(e)}

    def _run_automation_sync(self) -> Dict[str, Any]:
        """
        Synchronous method to run the survey automation.
        """
        try:
            with CPXSurveyAutomation(user_id=self.user_id, app_id=self.app_id) as automator:
                success = automator.complete_cpx_survey()
                
            return {
                "surveys_completed": 1 if success else 0,
                "total_earnings": 0.0, # Placeholder, needs implementation
                "duration_minutes": 0, # Placeholder, needs implementation
            }
        except Exception as e:
            logger.error(f"Exception in sync automation runner: {e}")
            return {"error": str(e)}