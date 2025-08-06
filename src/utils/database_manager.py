"""
Database Manager - Utility for handling database operations

Manages SQLite database operations for storing survey data, earnings, and bot statistics.
"""

import sqlite3
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from loguru import logger
import json


class DatabaseManager:
    """Manages database operations for the survey bot."""
    
    def __init__(self, db_url: str):
        """Initialize the database manager.
        
        Args:
            db_url: Database URL (SQLite file path)
        """
        self.db_url = db_url.replace('sqlite:///', '')
        self.connection = None
        
    async def initialize(self):
        """Initialize the database and create tables."""
        try:
            await self._create_tables()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    async def _create_tables(self):
        """Create database tables if they don't exist."""
        conn = await self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Surveys table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS surveys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    survey_id TEXT UNIQUE,
                    title TEXT,
                    earnings REAL,
                    duration INTEGER,
                    status TEXT,
                    completed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Earnings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS earnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL,
                    source TEXT,
                    status TEXT,
                    transaction_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tips table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id TEXT,
                    recipient_id TEXT,
                    amount REAL,
                    message TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Bot statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stat_name TEXT UNIQUE,
                    stat_value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Auto-collector logs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auto_collector_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    collection_time TIMESTAMP,
                    amount_collected REAL,
                    tips_found INTEGER,
                    status TEXT,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("Database tables created successfully")
        finally:
            conn.close()
    
    async def _get_connection(self):
        """Get a database connection."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_url)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    async def add_survey(self, survey_data: Dict[str, Any]) -> bool:
        """Add a new survey to the database.
        
        Args:
            survey_data: Survey information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = await self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO surveys 
                (survey_id, title, earnings, duration, status, completed_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                survey_data.get('survey_id'),
                survey_data.get('title'),
                survey_data.get('earnings', 0.0),
                survey_data.get('duration', 0),
                survey_data.get('status', 'pending'),
                survey_data.get('completed_at', datetime.now())
            ))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding survey: {e}")
            return False
    
    async def get_surveys(self, limit: int = 10, status: str = None) -> List[Dict[str, Any]]:
        """Get surveys from the database.
        
        Args:
            limit: Maximum number of surveys to return
            status: Filter by status
            
        Returns:
            List of survey dictionaries
        """
        try:
            conn = await self._get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM surveys"
            params = []
            
            if status:
                query += " WHERE status = ?"
                params.append(status)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting surveys: {e}")
            return []
    
    async def add_earning(self, amount: float, source: str, status: str = "pending") -> bool:
        """Add an earning record to the database.
        
        Args:
            amount: Earning amount
            source: Source of the earning
            status: Status of the earning
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = await self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO earnings (amount, source, status)
                VALUES (?, ?, ?)
            ''', (amount, source, status))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding earning: {e}")
            return False
    
    async def get_earnings(self, days: int = 30) -> Dict[str, float]:
        """Get earnings statistics.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary with earnings statistics
        """
        try:
            conn = await self._get_connection()
            cursor = conn.cursor()
            
            # Get total earnings
            cursor.execute('''
                SELECT SUM(amount) as total FROM earnings 
                WHERE status = 'completed'
            ''')
            total = cursor.fetchone()['total'] or 0.0
            
            # Get today's earnings
            today = datetime.now().date()
            cursor.execute('''
                SELECT SUM(amount) as today FROM earnings 
                WHERE status = 'completed' AND DATE(created_at) = ?
            ''', (today,))
            today_earnings = cursor.fetchone()['today'] or 0.0
            
            # Get this week's earnings
            week_ago = datetime.now() - timedelta(days=7)
            cursor.execute('''
                SELECT SUM(amount) as week FROM earnings 
                WHERE status = 'completed' AND created_at >= ?
            ''', (week_ago,))
            week_earnings = cursor.fetchone()['week'] or 0.0
            
            return {
                'total': total,
                'today': today_earnings,
                'week': week_earnings
            }
        except Exception as e:
            logger.error(f"Error getting earnings: {e}")
            return {'total': 0.0, 'today': 0.0, 'week': 0.0}
    
    async def add_tip(self, sender_id: str, recipient_id: str, amount: float, message: str = "") -> bool:
        """Add a tip record to the database.
        
        Args:
            sender_id: Discord ID of the sender
            recipient_id: Discord ID of the recipient
            amount: Tip amount
            message: Optional message
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = await self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tips (sender_id, recipient_id, amount, message, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (sender_id, recipient_id, amount, message, 'sent'))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding tip: {e}")
            return False
    
    async def get_tip_stats(self, user_id: str) -> Dict[str, Any]:
        """Get tip statistics for a user.
        
        Args:
            user_id: Discord user ID
            
        Returns:
            Dictionary with tip statistics
        """
        try:
            conn = await self._get_connection()
            cursor = conn.cursor()
            
            # Get tips sent
            cursor.execute('''
                SELECT COUNT(*) as count, SUM(amount) as total 
                FROM tips WHERE sender_id = ? AND status = 'sent'
            ''', (user_id,))
            sent = cursor.fetchone()
            
            # Get tips received
            cursor.execute('''
                SELECT COUNT(*) as count, SUM(amount) as total 
                FROM tips WHERE recipient_id = ? AND status = 'sent'
            ''', (user_id,))
            received = cursor.fetchone()
            
            return {
                'tips_sent': sent['count'] or 0,
                'tips_received': received['count'] or 0,
                'amount_sent': sent['total'] or 0.0,
                'amount_received': received['total'] or 0.0
            }
        except Exception as e:
            logger.error(f"Error getting tip stats: {e}")
            return {'tips_sent': 0, 'tips_received': 0, 'amount_sent': 0.0, 'amount_received': 0.0}
    
    async def update_bot_stat(self, stat_name: str, stat_value: Any):
        """Update a bot statistic.
        
        Args:
            stat_name: Name of the statistic
            stat_value: Value of the statistic
        """
        try:
            conn = await self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO bot_stats (stat_name, stat_value, updated_at)
                VALUES (?, ?, ?)
            ''', (stat_name, json.dumps(stat_value), datetime.now()))
            conn.commit()
        except Exception as e:
            logger.error(f"Error updating bot stat: {e}")
    
    async def get_bot_stat(self, stat_name: str) -> Any:
        """Get a bot statistic.
        
        Args:
            stat_name: Name of the statistic
            
        Returns:
            Statistic value
        """
        try:
            conn = await self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT stat_value FROM bot_stats WHERE stat_name = ?
            ''', (stat_name,))
            row = cursor.fetchone()
            
            if row:
                return json.loads(row['stat_value'])
            return None
        except Exception as e:
            logger.error(f"Error getting bot stat: {e}")
            return None
    
    async def add_auto_collector_log(self, amount_collected: float, tips_found: int, status: str, error_message: str = None):
        """Add an auto-collector log entry.
        
        Args:
            amount_collected: Amount collected
            tips_found: Number of tips found
            status: Status of the collection
            error_message: Error message if any
        """
        try:
            conn = await self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO auto_collector_logs 
                (collection_time, amount_collected, tips_found, status, error_message)
                VALUES (?, ?, ?, ?, ?)
            ''', (datetime.now(), amount_collected, tips_found, status, error_message))
            conn.commit()
        except Exception as e:
            logger.error(f"Error adding auto-collector log: {e}")
    
    async def get_auto_collector_stats(self) -> Dict[str, Any]:
        """Get auto-collector statistics.
        
        Returns:
            Dictionary with auto-collector statistics
        """
        try:
            conn = await self._get_connection()
            cursor = conn.cursor()
            
            # Get total collected
            cursor.execute('''
                SELECT SUM(amount_collected) as total, COUNT(*) as collections
                FROM auto_collector_logs WHERE status = 'success'
            ''')
            stats = cursor.fetchone()
            
            # Get last collection
            cursor.execute('''
                SELECT collection_time FROM auto_collector_logs 
                WHERE status = 'success' ORDER BY collection_time DESC LIMIT 1
            ''')
            last_collection = cursor.fetchone()
            
            return {
                'total_collected': stats['total'] or 0.0,
                'total_collections': stats['collections'] or 0,
                'last_collection': last_collection['collection_time'] if last_collection else None
            }
        except Exception as e:
            logger.error(f"Error getting auto-collector stats: {e}")
            return {'total_collected': 0.0, 'total_collections': 0, 'last_collection': None}
    
    async def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None 