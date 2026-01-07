"""
Main orchestration script for Asana seed data generation.
Coordinates database creation, data generation, and consistency validation.
"""

import logging
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import uuid

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models import (
    Organization, Team, User, TeamMember, Project, ProjectMember,
    Section, Tag, Task, Comment, TeamType, ProjectType
)
from scrapers import CompanyNameScraper, UserNameScraper
from generators import (
    UserGenerator, ProjectGenerator, TaskGenerator, 
    CommentGenerator, TagGenerator
)
from utils import DatabaseManager, DateGenerator, TemporalConsistencyValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AsanaDataSimulator:
    """Main orchestrator for Asana seed data generation."""

    def __init__(
        self,
        db_path: str = "output/asana_simulation.sqlite",
        num_employees: int = 5000,
        num_projects: int = 350,
        tasks_per_project: int = 71
    ):
        """
        Initialize simulator.
        
        Args:
            db_path: Path to SQLite database
            num_employees: Number of employees to simulate (default: 5000 for enterprise org)
            num_projects: Number of projects to create (default: 350 across 15+ teams)
            tasks_per_project: Average tasks per project (default: 71 for ~25,000 tasks total)
        """
        self.db_path = db_path
        self.num_employees = num_employees
        self.num_projects = num_projects
        self.tasks_per_project = tasks_per_project
        
        self.db = DatabaseManager(db_path)
        self.organization_id = str(uuid.uuid4())
        self.user_ids = []
        self.team_ids = []
        self.project_ids = []

    def run(self) -> None:
        """Execute full data generation pipeline."""
        try:
            logger.info("Starting Asana data simulation...")
            
            # Initialize database
            self._initialize_database()
            
            # Generate base entities
            self._generate_organizations()
            self._generate_teams()
            self._generate_users()
            self._generate_team_memberships()
            
            # Generate work entities
            self._generate_projects()
            self._generate_project_members()
            self._generate_tasks()
            self._generate_comments()
            self._generate_tags()
            self._generate_task_tags()
            
            # Validate consistency
            self._validate_data()
            
            # Print summary
            self._print_summary()
            
            logger.info("Data generation completed successfully!")
            
        except Exception as e:
            logger.error(f"Error during data generation: {e}", exc_info=True)
            raise
        finally:
            self.db.close()

    def _initialize_database(self) -> None:
        """Initialize database schema."""
        logger.info("Initializing database schema...")
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(self.db_path) or '.', exist_ok=True)
        
        # Connect to database
        self.db.connect()
        
        # Load and execute schema - look in parent directory of src
        project_root = os.path.dirname(os.path.dirname(__file__))
        schema_path = os.path.join(project_root, 'schema.sql')
        
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        self.db.execute_script(schema)
        logger.info("Database schema initialized")

    def _generate_organizations(self) -> None:
        """Generate organization - Asana Inc. Workspace"""
        logger.info("Generating organization...")
        
        # Simulate Asana Inc. - the actual company
        org_data = {
            "organization_id": self.organization_id,
            "name": "Asana Inc.",
            "domain": "asana.com",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "employee_count": self.num_employees,
            "industry": "Enterprise Software",
            "location": "San Francisco, CA",
            "is_verified": 1,
        }
        
        self.db.insert_one("organizations", org_data)
        logger.info(f"Created organization: Asana Inc.")

    def _generate_teams(self) -> None:
        """Generate teams within organization."""
        logger.info("Generating teams...")
        
        # Asana Inc. - Realistic team structure based on their actual organization
        asana_teams = [
            # Engineering Teams (40% of company)
            ("Core Platform Team", "engineering", "Building Asana's core product infrastructure"),
            ("Web Platform Team", "engineering", "Web application development and optimization"),
            ("Mobile Team", "engineering", "iOS and Android mobile applications"),
            ("Backend Services Team", "engineering", "Microservices and API development"),
            ("DevOps & Infrastructure", "engineering", "Cloud infrastructure and deployment"),
            ("Quality Assurance", "engineering", "Testing and quality assurance"),
            
            # Product Teams (15% of company)
            ("Product Management", "product", "Product strategy and roadmap"),
            ("Design Systems", "product", "UI/UX design and component libraries"),
            ("Product Design", "product", "Feature design and user experience"),
            ("Product Analytics", "product", "Analytics and data-driven insights"),
            
            # Go-to-Market Teams (20% of company)
            ("Sales Engineering", "sales", "Pre-sales technical support"),
            ("Enterprise Sales", "sales", "Large account sales management"),
            ("Mid-Market Sales", "sales", "Mid-market accounts"),
            ("Sales Operations", "sales", "Sales tools and processes"),
            ("Marketing Communications", "marketing", "Content and brand marketing"),
            ("Product Marketing", "marketing", "Product positioning and messaging"),
            ("Growth & Demand Gen", "marketing", "User acquisition and growth"),
            
            # Operations & Support (20% of company)
            ("Customer Success", "operations", "Customer onboarding and support"),
            ("Technical Support", "operations", "Technical customer support"),
            ("Finance & Accounting", "operations", "Financial management"),
            ("Human Resources", "operations", "People operations and hiring"),
            ("Legal & Compliance", "operations", "Legal and regulatory compliance"),
            ("Business Operations", "operations", "Process optimization"),
        ]
        
        teams_data = []
        
        for name, team_type, description in asana_teams:
            team_id = str(uuid.uuid4())
            self.team_ids.append(team_id)
            
            # Map to our enum
            type_mapping = {
                "engineering": TeamType.ENGINEERING.value,
                "product": TeamType.PRODUCT.value,
                "sales": TeamType.SALES.value,
                "marketing": TeamType.MARKETING.value,
                "operations": TeamType.OPERATIONS.value,
            }
            
            teams_data.append({
                "team_id": team_id,
                "organization_id": self.organization_id,
                "name": name,
                "description": description,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "team_type": type_mapping[team_type],
            })
        
        self.db.insert_many("teams", teams_data)
        logger.info(f"Created {len(teams_data)} teams")

    def _generate_users(self) -> None:
        """Generate users."""
        logger.info(f"Generating {self.num_employees} users...")
        
        users_data = UserGenerator.generate_users(
            self.organization_id,
            count=self.num_employees
        )
        
        self.db.insert_many("users", users_data)
        self.user_ids = [u["user_id"] for u in users_data]
        
        logger.info(f"Created {len(self.user_ids)} users")

    def _generate_team_memberships(self) -> None:
        """Generate team memberships."""
        logger.info("Generating team memberships...")
        
        memberships = []
        
        # Distribute users across teams
        users_per_team = self.num_employees // len(self.team_ids)
        
        for team_id in self.team_ids:
            # Select subset of users for this team
            team_users = self.user_ids[
                len(memberships):(len(memberships) + users_per_team)
            ]
            
            for user_id in team_users:
                memberships.append({
                    "team_member_id": str(uuid.uuid4()),
                    "team_id": team_id,
                    "user_id": user_id,
                    "joined_at": datetime.utcnow().isoformat(),
                    "role": "member",
                    "is_active": 1,
                })
        
        self.db.insert_many("team_members", memberships)
        logger.info(f"Created {len(memberships)} team memberships")

    def _generate_projects(self) -> None:
        """Generate projects with sections."""
        logger.info(f"Generating {self.num_projects} projects...")
        
        projects, sections_dict = ProjectGenerator.generate_projects(
            self.organization_id,
            self.team_ids,
            self.user_ids,
            count=self.num_projects
        )
        
        self.db.insert_many("projects", projects)
        self.project_ids = [p["project_id"] for p in projects]
        
        # Insert sections
        all_sections = []
        for project_id, sections in sections_dict.items():
            all_sections.extend(sections)
        
        self.db.insert_many("sections", all_sections)
        
        logger.info(f"Created {len(projects)} projects with {len(all_sections)} sections")

    def _generate_project_members(self) -> None:
        """Generate project members."""
        logger.info("Generating project members...")
        
        members = []
        
        for project_id in self.project_ids:
            # 70-90% of team members in a project
            num_members = int(len(self.user_ids) * (0.7 + 0.2 * __import__('random').random()))
            project_users = __import__('random').sample(self.user_ids, num_members)
            
            for user_id in project_users:
                members.append({
                    "project_member_id": str(uuid.uuid4()),
                    "project_id": project_id,
                    "user_id": user_id,
                    "added_at": datetime.utcnow().isoformat(),
                    "role": "member",
                })
        
        self.db.insert_many("project_members", members)
        logger.info(f"Created {len(members)} project members")

    def _generate_tasks(self) -> None:
        """Generate tasks for projects."""
        logger.info(f"Generating tasks (~{self.num_projects * self.tasks_per_project} total)...")
        
        all_tasks = []
        
        for project_id in self.project_ids:
            # Get sections for this project
            try:
                sections = self.db.connection.execute(
                    "SELECT section_id FROM sections WHERE project_id = ?",
                    (project_id,)
                ).fetchall()
                section_ids = [s['section_id'] for s in sections]
            except:
                section_ids = []
            
            if not section_ids:
                continue
            
            # Generate tasks
            tasks = TaskGenerator.generate_tasks(
                project_id,
                section_ids,
                self.user_ids,
                __import__('random').choice(self.user_ids),
                count=self.tasks_per_project
            )
            
            all_tasks.extend(tasks)
        
        self.db.insert_many("tasks", all_tasks)
        logger.info(f"Created {len(all_tasks)} tasks")

    def _generate_comments(self) -> None:
        """Generate comments on tasks."""
        logger.info("Generating comments...")
        
        all_comments = []
        
        # Get sample of tasks
        tasks = self.db.get_all("tasks", limit=min(500, self.num_projects * self.tasks_per_project))
        
        for task in tasks:
            comments = CommentGenerator.generate_comments(
                task["task_id"],
                task["created_by"],
                self.user_ids,
                datetime.fromisoformat(task["created_at"]),
                datetime.fromisoformat(task["completed_at"]) if task["completed_at"] else None,
                task_name=task.get("name")  # Pass task name for LLM enhancement
            )
            all_comments.extend(comments)
        
        if all_comments:
            self.db.insert_many("comments", all_comments)
        
        logger.info(f"Created {len(all_comments)} comments")

    def _generate_tags(self) -> None:
        """Generate tags."""
        logger.info("Generating tags...")
        
        tags = TagGenerator.generate_tags(
            self.organization_id,
            __import__('random').choice(self.user_ids)
        )
        
        self.db.insert_many("tags", tags)
        logger.info(f"Created {len(tags)} tags")

    def _generate_task_tags(self) -> None:
        """Assign tags to tasks."""
        logger.info("Generating task-tag associations...")
        
        all_task_tags = []
        
        # Get all tags and sample of tasks
        tags = self.db.get_all("tags")
        tasks = self.db.get_all("tasks", limit=min(500, self.num_projects * self.tasks_per_project))
        
        if not tags:
            return
        
        for task in tasks:
            # Each task gets 0-3 tags
            num_tags = __import__('random').randint(0, 3)
            selected_tags = __import__('random').sample(tags, min(num_tags, len(tags)))
            
            for tag in selected_tags:
                all_task_tags.append({
                    "task_tag_id": str(uuid.uuid4()),
                    "task_id": task["task_id"],
                    "tag_id": tag["tag_id"],
                    "added_at": datetime.utcnow().isoformat(),
                })
        
        if all_task_tags:
            self.db.insert_many("task_tags", all_task_tags)
        
        logger.info(f"Created {len(all_task_tags)} task-tag associations")

    def _validate_data(self) -> None:
        """Validate data consistency."""
        logger.info("Validating data consistency...")
        
        # Check referential integrity
        try:
            # Sample check: verify all tasks reference valid projects
            result = self.db.connection.execute("""
                SELECT COUNT(*) as invalid FROM tasks 
                WHERE project_id NOT IN (SELECT project_id FROM projects)
            """).fetchone()
            
            if result['invalid'] > 0:
                logger.warning(f"Found {result['invalid']} tasks with invalid project_id")
            
            # Check temporal consistency
            result = self.db.connection.execute("""
                SELECT COUNT(*) as invalid FROM tasks 
                WHERE completed_at IS NOT NULL AND completed_at < created_at
            """).fetchone()
            
            if result['invalid'] > 0:
                logger.warning(f"Found {result['invalid']} tasks with invalid timestamps")
            
            logger.info("Data validation completed")
            
        except Exception as e:
            logger.error(f"Validation error: {e}")

    def _print_summary(self) -> None:
        """Print summary of generated data."""
        logger.info("\n" + "="*60)
        logger.info("DATA GENERATION SUMMARY")
        logger.info("="*60)
        
        try:
            tables = [
                "organizations", "teams", "users", "team_members",
                "projects", "sections", "tasks", "comments", "tags", "task_tags"
            ]
            
            for table in tables:
                count = self.db.get_count(table)
                logger.info(f"  {table:<20} : {count:>6} records")
            
            logger.info("="*60)
            logger.info(f"Database file: {os.path.abspath(self.db_path)}")
            logger.info("="*60 + "\n")
            
        except Exception as e:
            logger.error(f"Error printing summary: {e}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate realistic asana.com seed data (enterprise scale)"
    )
    parser.add_argument(
        "--db",
        default="output/asana_simulation.sqlite",
        help="Path to output database file"
    )
    parser.add_argument(
        "--employees",
        type=int,
        default=5000,
        help="Number of employees to simulate (default: 5000 for enterprise org)"
    )
    parser.add_argument(
        "--projects",
        type=int,
        default=350,
        help="Number of projects to create (default: 350)"
    )
    parser.add_argument(
        "--tasks-per-project",
        type=int,
        default=71,
        help="Average number of tasks per project (default: 71 for ~25,000 tasks)"
    )
    
    args = parser.parse_args()
    
    simulator = AsanaDataSimulator(
        db_path=args.db,
        num_employees=args.employees,
        num_projects=args.projects,
        tasks_per_project=args.tasks_per_project
    )
    
    simulator.run()


if __name__ == "__main__":
    main()
