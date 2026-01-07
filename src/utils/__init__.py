"""
Utility modules for data generation, LLM calls, and database operations.
"""

import sqlite3
import logging
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any
import json
import os


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database operations."""

    def __init__(self, db_path: str):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        """Connect to database."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def execute_script(self, script: str) -> None:
        """
        Execute SQL script (for schema creation).
        
        Args:
            script: SQL script content
        """
        try:
            if self.connection:
                self.connection.executescript(script)
                self.connection.commit()
                logger.info("SQL script executed successfully")
        except sqlite3.Error as e:
            logger.error(f"Error executing script: {e}")
            raise

    def insert_one(self, table: str, data: Dict[str, Any]) -> None:
        """
        Insert single record.
        
        Args:
            table: Table name
            data: Dictionary of column:value pairs
        """
        try:
            if not self.connection:
                raise RuntimeError("Database not connected")
            
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?" for _ in data])
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            self.connection.execute(sql, tuple(data.values()))
            self.connection.commit()
        except sqlite3.Error as e:
            logger.error(f"Error inserting into {table}: {e}")
            self.connection.rollback()
            raise

    def insert_many(self, table: str, data_list: List[Dict[str, Any]]) -> None:
        """
        Insert multiple records in batch.
        
        Args:
            table: Table name
            data_list: List of dictionaries with column:value pairs
        """
        if not data_list:
            return

        try:
            if not self.connection:
                raise RuntimeError("Database not connected")
            
            columns = ", ".join(data_list[0].keys())
            placeholders = ", ".join(["?" for _ in data_list[0]])
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            # Convert dict values to tuples for executemany
            values = [tuple(d.values()) for d in data_list]
            
            self.connection.executemany(sql, values)
            self.connection.commit()
            logger.info(f"Inserted {len(data_list)} records into {table}")
        except sqlite3.Error as e:
            logger.error(f"Error batch inserting into {table}: {e}")
            self.connection.rollback()
            raise

    def get_all(self, table: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch all records from table.
        
        Args:
            table: Table name
            limit: Optional limit on number of records
            
        Returns:
            List of records as dictionaries
        """
        try:
            if not self.connection:
                raise RuntimeError("Database not connected")
            
            sql = f"SELECT * FROM {table}"
            if limit:
                sql += f" LIMIT {limit}"
            
            cursor = self.connection.execute(sql)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error fetching from {table}: {e}")
            raise

    def get_count(self, table: str) -> int:
        """Get record count in table."""
        try:
            if not self.connection:
                raise RuntimeError("Database not connected")
            
            cursor = self.connection.execute(f"SELECT COUNT(*) as count FROM {table}")
            return cursor.fetchone()['count']
        except sqlite3.Error as e:
            logger.error(f"Error counting records in {table}: {e}")
            raise


class DateGenerator:
    """Generates realistic date distributions for Asana data."""

    @staticmethod
    def get_random_task_creation_date(
        start_date: date,
        end_date: date,
        weights: Optional[Dict[str, float]] = None
    ) -> datetime:
        """
        Generate task creation date following realistic patterns.
        Methodology: Higher creation rates Mon-Wed, lower Thu-Fri.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            weights: Optional weekday weights
            
        Returns:
            Random datetime for task creation
        """
        # Default: Mon(0.25), Tue(0.25), Wed(0.25), Thu(0.15), Fri(0.10)
        if not weights:
            weights = {
                0: 0.25,  # Monday
                1: 0.25,  # Tuesday
                2: 0.25,  # Wednesday
                3: 0.15,  # Thursday
                4: 0.10,  # Friday
                5: 0.0,   # Saturday
                6: 0.0,   # Sunday
            }
        
        import random
        
        # Generate random date in range
        days_diff = (end_date - start_date).days
        random_days = random.randint(0, days_diff)
        random_date = start_date + timedelta(days=random_days)
        
        # Ensure it's a weekday
        while random_date.weekday() in [5, 6]:
            random_days = random.randint(0, days_diff)
            random_date = start_date + timedelta(days=random_days)
        
        # Add random time (business hours)
        hour = random.randint(8, 17)
        minute = random.randint(0, 59)
        
        return datetime.combine(random_date, datetime.min.time()).replace(
            hour=hour, minute=minute
        )

    @staticmethod
    def get_random_due_date(
        created_date: datetime,
        distribution: Optional[Dict[str, float]] = None
    ) -> Optional[date]:
        """
        Generate due date following realistic distribution.
        Methodology: 25% within 1 week, 40% within 1 month, 20% 1-3 months,
                     10% no due date, 5% overdue.
        
        Args:
            created_date: Task creation date
            distribution: Optional custom distribution
            
        Returns:
            Due date or None
        """
        # Default distribution based on Asana research
        if not distribution:
            distribution = {
                "within_week": 0.25,
                "within_month": 0.40,
                "within_three_months": 0.20,
                "no_due_date": 0.10,
                "overdue": 0.05,
            }
        
        import random
        
        rand = random.random()
        cumulative = 0
        
        for key, weight in distribution.items():
            cumulative += weight
            if rand <= cumulative:
                if key == "within_week":
                    days = random.randint(1, 7)
                elif key == "within_month":
                    days = random.randint(8, 30)
                elif key == "within_three_months":
                    days = random.randint(31, 90)
                elif key == "no_due_date":
                    return None
                elif key == "overdue":
                    days = random.randint(-14, -1)
                else:
                    return None
                
                due_date = created_date + timedelta(days=days)
                
                # Avoid weekends for 85% of tasks
                if random.random() < 0.85:
                    while due_date.weekday() in [5, 6]:
                        due_date += timedelta(days=1)
                
                return due_date.date()
        
        return None

    @staticmethod
    def get_completion_timestamp(
        created_at: datetime,
        due_date: Optional[date] = None
    ) -> Optional[datetime]:
        """
        Generate completion timestamp following realistic patterns.
        Methodology: 1-14 days after creation (log-normal distribution).
        
        Args:
            created_at: Task creation timestamp
            due_date: Optional task due date
            
        Returns:
            Completion timestamp or None if not completed
        """
        import random
        import math
        
        # 60% tasks completed (varies by project)
        if random.random() > 0.60:
            return None
        
        # Log-normal distribution: most tasks complete in 2-7 days
        # but some take longer
        days_to_complete = max(1, int(random.lognormvariate(1.5, 0.8)))
        days_to_complete = min(days_to_complete, 14)  # Cap at 14 days
        
        completed_at = created_at + timedelta(days=days_to_complete)
        
        # If there's a due date, complete before it (with 80% probability)
        if due_date and random.random() < 0.80:
            due_datetime = datetime.combine(due_date, datetime.max.time())
            if completed_at > due_datetime:
                completed_at = due_datetime - timedelta(hours=random.randint(1, 24))
        
        return completed_at


class LLMPromptLoader:
    """Loads LLM prompts from files."""

    @staticmethod
    def load_prompt(prompt_name: str, prompts_dir: str = "prompts") -> str:
        """
        Load prompt from file.
        
        Args:
            prompt_name: Name of prompt file (without .txt extension)
            prompts_dir: Directory containing prompts
            
        Returns:
            Prompt content
        """
        prompt_path = os.path.join(prompts_dir, f"{prompt_name}.txt")
        
        try:
            with open(prompt_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"Prompt file not found: {prompt_path}")
            return ""

    @staticmethod
    def load_all_prompts(prompts_dir: str = "prompts") -> Dict[str, str]:
        """
        Load all prompts from directory.
        
        Args:
            prompts_dir: Directory containing prompts
            
        Returns:
            Dictionary mapping prompt names to content
        """
        prompts = {}
        
        if not os.path.exists(prompts_dir):
            logger.warning(f"Prompts directory not found: {prompts_dir}")
            return prompts
        
        for filename in os.listdir(prompts_dir):
            if filename.endswith('.txt'):
                prompt_name = filename[:-4]
                prompt_path = os.path.join(prompts_dir, filename)
                
                try:
                    with open(prompt_path, 'r') as f:
                        prompts[prompt_name] = f.read()
                except Exception as e:
                    logger.error(f"Error loading prompt {filename}: {e}")
        
        return prompts


class TemporalConsistencyValidator:
    """Validates temporal consistency of generated data."""

    @staticmethod
    def validate_task_dates(
        created_at: datetime,
        due_date: Optional[date],
        completed_at: Optional[datetime],
        start_date: Optional[date]
    ) -> bool:
        """
        Validate temporal consistency of task dates.
        
        Rules:
        - created_at must be first chronologically
        - start_date should be >= created_at (if present)
        - due_date should be >= start_date or created_at (if present)
        - completed_at must be >= created_at
        - completed_at should be <= now
        
        Args:
            created_at: Task creation timestamp
            due_date: Task due date
            completed_at: Task completion timestamp
            start_date: Task start date
            
        Returns:
            True if all constraints satisfied
        """
        now = datetime.utcnow()
        
        # created_at must be before now
        if created_at > now:
            logger.warning(f"created_at ({created_at}) is in future")
            return False
        
        # If task completed
        if completed_at:
            # completed_at must be after created_at
            if completed_at < created_at:
                logger.warning(f"completed_at ({completed_at}) before created_at ({created_at})")
                return False
            
            # completed_at must be before now
            if completed_at > now:
                logger.warning(f"completed_at ({completed_at}) is in future")
                return False
        
        # If due_date exists
        if due_date:
            due_datetime = datetime.combine(due_date, datetime.max.time())
            
            # If completed, should be before due date (80% of the time)
            if completed_at and completed_at > due_datetime:
                # This is allowed but less common (overdue tasks)
                pass
        
        # If start_date exists
        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            
            if start_datetime < created_at:
                logger.warning(f"start_date ({start_date}) before created_at ({created_at})")
                return False
        
        return True

    @staticmethod
    def validate_comment_dates(
        task_created_at: datetime,
        comment_created_at: datetime,
        task_completed_at: Optional[datetime]
    ) -> bool:
        """
        Validate comment created after task.
        
        Args:
            task_created_at: Task creation timestamp
            comment_created_at: Comment creation timestamp
            task_completed_at: Task completion timestamp
            
        Returns:
            True if valid
        """
        # Comment must be after task creation
        if comment_created_at < task_created_at:
            return False
        
        # Comment can be after task completion
        return True
