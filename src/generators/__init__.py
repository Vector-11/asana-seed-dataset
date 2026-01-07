"""
Data generators for Asana simulation entities.
Implements realistic data generation with proper distributions and patterns.
Optionally enhanced with Groq LLM for realistic content generation.
"""

import random
import uuid
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Import LLM enhancer (graceful fallback if not available)
try:
    from llm_enhancer import enhance_task_description, enhance_comment
except ImportError:
    def enhance_task_description(task_name, project_type):
        return None
    def enhance_comment(task_name, user_role):
        return None


class UserGenerator:
    """
    Generates realistic user data.
    Methodology: Uses name lists from census data reflecting demographic distributions.
    """

    FIRST_NAMES_MALE = [
        "James", "Robert", "Michael", "John", "David", "Richard", "Charles",
        "Joseph", "Thomas", "Christopher", "Daniel", "Matthew", "Anthony",
        "Mark", "Donald", "Steven", "Brian", "Paul", "Andrew", "Joshua"
    ]

    FIRST_NAMES_FEMALE = [
        "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan",
        "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Betty", "Margaret",
        "Sandra", "Ashley", "Kimberly", "Emily", "Donna", "Michelle"
    ]

    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
        "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    ]

    DEPARTMENTS = [
        "Engineering", "Product", "Marketing", "Sales", "Operations",
        "Design", "Finance", "HR", "Support", "DevOps"
    ]

    ROLES = [
        "Manager", "Senior Engineer", "Engineer", "Lead", "Analyst",
        "Director", "Coordinator", "Specialist", "Developer", "Designer"
    ]

    @classmethod
    def generate_users(
        cls,
        organization_id: str,
        count: int = 100,
        start_date: datetime = None
    ) -> List[Dict]:
        """
        Generate realistic user records.
        
        Args:
            organization_id: Organization ID for users
            count: Number of users to generate
            start_date: Organization creation date (users joined after this)
            
        Returns:
            List of user dictionaries ready for database insertion
        """
        if start_date is None:
            start_date = datetime.utcnow() - timedelta(days=180)
        
        users = []
        used_emails = set()
        
        for i in range(count):
            # 50-50 gender split
            if random.random() < 0.5:
                first_name = random.choice(cls.FIRST_NAMES_MALE)
            else:
                first_name = random.choice(cls.FIRST_NAMES_FEMALE)
            
            last_name = random.choice(cls.LAST_NAMES)
            
            # Generate unique email
            base_email = f"{first_name.lower()}.{last_name.lower()}"
            email = base_email
            counter = 1
            while email in used_emails:
                email = f"{base_email}{counter}"
                counter += 1
            
            used_emails.add(email)
            
            # Realistic joined date (within organization history)
            days_ago = random.randint(1, 180)
            joined_date = datetime.utcnow() - timedelta(days=days_ago)
            
            # created_at should be shortly after user joined (within a few days for onboarding)
            # This represents when their Asana account was actually created in the system
            days_after_join = random.randint(0, 3)  # Account created 0-3 days after joining
            created_at = joined_date + timedelta(days=days_after_join)
            
            # updated_at should be later (when user profile was last modified)
            # Most users: no recent updates (20% have updates in last 30 days)
            if random.random() < 0.2:
                # Recently updated user
                hours_since_creation = random.randint(1, 30 * 24)
            else:
                # Not recently updated - distributed across their tenure
                hours_since_creation = random.randint(0, int((datetime.utcnow() - created_at).total_seconds() / 3600))
            
            updated_at = created_at + timedelta(hours=hours_since_creation)
            
            # 5% admins, 20% inactive
            is_admin = random.random() < 0.05
            is_active = random.random() < 0.95
            
            user = {
                "user_id": str(uuid.uuid4()),
                "organization_id": organization_id,
                "email": f"{email}@asana-sim.com",
                "name": f"{first_name} {last_name}",
                "first_name": first_name,
                "last_name": last_name,
                "avatar_url": f"https://avatars.example.com/{email}.jpg",
                "phone": f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
                "created_at": created_at.isoformat(),
                "updated_at": updated_at.isoformat(),
                "is_active": is_active,
                "is_admin": is_admin,
                "department": random.choice(cls.DEPARTMENTS),
                "role": random.choice(cls.ROLES),
                "joined_date": joined_date.isoformat(),
            }
            users.append(user)
        
        logger.info(f"Generated {len(users)} users")
        return users


class ProjectGenerator:
    """
    Generates realistic project data.
    Methodology: Based on project types and team structures in real SaaS companies.
    """

    PROJECT_TYPES = ["sprint", "ongoing", "bug_tracking", "marketing_campaign", "ops_initiative"]
    
    PROJECT_TEMPLATES = {
        "sprint": {
            "names": [
                "Asana AI Feature Development", "Timeline Feature Enhancement",
                "Board View Optimization", "Portfolio View Improvements",
                "Mobile App Sprint 1", "API v3 Development",
                "Database Performance Upgrade", "Security Hardening Initiative",
                "Webhook Infrastructure", "Custom Fields Enhancement",
                "Goal Management System", "Integration Framework",
                "Notification Engine Redesign", "Collaboration Features",
                "Export/Import Capabilities", "Search and Filtering"
            ],
            "descriptions": [
                "Development sprint for Asana core platform features",
                "Sprint dedicated to product improvements and technical debt",
                "Major feature implementation for work management",
                "New capability development sprint for Asana platform"
            ]
        },
        "ongoing": {
            "names": [
                "Asana Product Roadmap", "Customer Success Operations",
                "QA & Platform Testing", "Documentation & Support",
                "Code Quality & Review", "Monitoring & Performance",
                "Integration Management", "API Maintenance"
            ],
            "descriptions": [
                "Ongoing work for continuous Asana platform improvement",
                "Regular maintenance and support for Asana services",
                "Operational excellence for work management platform"
            ]
        },
        "bug_tracking": {
            "names": [
                "Platform Bug Tracker", "Critical Issues & Fixes",
                "Quality Assurance Testing", "Performance Issues",
                "Security Vulnerabilities"
            ],
            "descriptions": [
                "Central repository for tracking and fixing platform bugs",
                "Critical issue triage and resolution"
            ]
        },
        "marketing_campaign": {
            "names": [
                "Q1 2025 - Asana AI Launch", "Campaign Management Use Case",
                "Content Marketing Initiative", "Social Media Strategy 2025",
                "Email Nurture Campaign", "Partner Marketing Program",
                "Creative Production Campaign", "Goal Management Promotion"
            ],
            "descriptions": [
                "Coordinated marketing effort for Asana feature launch",
                "Use case promotion and customer education campaign",
                "Marketing campaign utilizing Asana's own platform"
            ]
        },
        "ops_initiative": {
            "names": [
                "Infrastructure Scaling", "Process Automation Initiative",
                "Team Expansion Program", "Systems Integration",
                "Customer Onboarding Improvement", "Support System Upgrade",
                "HR Process Automation", "Finance System Upgrade"
            ],
            "descriptions": [
                "Operational initiative for Asana business improvement",
                "Internal process optimization using Asana platform",
                "Organizational scaling and efficiency initiative"
            ]
        }
    }

    DEFAULT_SECTIONS = {
        "sprint": ["Backlog", "To Do", "In Progress", "In Review", "Done"],
        "ongoing": ["Backlog", "In Progress", "Done"],
        "bug_tracking": ["New", "Assigned", "In Progress", "Blocked", "Ready for QA", "Closed"],
        "marketing_campaign": ["Planning", "In Progress", "Review", "Published"],
        "ops_initiative": ["Planning", "In Progress", "Testing", "Complete"],
    }

    @classmethod
    def generate_projects(
        cls,
        organization_id: str,
        team_ids: List[str],
        user_ids: List[str],
        count: int = 30
    ) -> Tuple[List[Dict], Dict[str, List[Dict]]]:
        """
        Generate realistic projects with sections.
        
        Args:
            organization_id: Organization ID
            team_ids: List of team IDs
            user_ids: List of user IDs for assignment
            count: Number of projects to generate
            
        Returns:
            Tuple of (projects list, sections dict by project_id)
        """
        projects = []
        sections_by_project = {}
        used_names = set()
        
        for i in range(count):
            project_type = random.choice(cls.PROJECT_TYPES)
            template = cls.PROJECT_TEMPLATES[project_type]
            
            project_id = str(uuid.uuid4())
            created_by = random.choice(user_ids)
            
            # Ensure unique project names
            project_name = random.choice(template["names"])
            counter = 1
            while project_name in used_names:
                project_name = f"{random.choice(template['names'])} {counter}"
                counter += 1
            used_names.add(project_name)
            
            # Sprint projects have defined dates, others are open-ended
            if project_type == "sprint":
                start_date = (datetime.utcnow() - timedelta(days=random.randint(0, 180))).date()
                end_date = start_date + timedelta(days=14)
            else:
                start_date = (datetime.utcnow() - timedelta(days=random.randint(30, 180))).date()
                end_date = None if random.random() < 0.5 else start_date + timedelta(days=random.randint(30, 180))
            
            project = {
                "project_id": project_id,
                "organization_id": organization_id,
                "team_id": random.choice(team_ids) if random.random() < 0.8 else None,
                "name": project_name,
                "description": random.choice(template["descriptions"]),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": (datetime.utcnow() + timedelta(hours=random.randint(0, 48))).isoformat(),
                "created_by": created_by,
                "archived_at": None,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat() if end_date else None,
                "status": "active" if random.random() < 0.8 else "archived",
                "project_type": project_type,
                "visibility": "team" if random.random() < 0.7 else "private",
            }
            projects.append(project)
            
            # Generate sections for this project
            sections = []
            section_names = cls.DEFAULT_SECTIONS[project_type]
            
            for order, section_name in enumerate(section_names):
                section = {
                    "section_id": str(uuid.uuid4()),
                    "project_id": project_id,
                    "name": section_name,
                    "description": None,
                    "created_at": project["created_at"],
                    "display_order": order,
                }
                sections.append(section)
            
            sections_by_project[project_id] = sections
        
        logger.info(f"Generated {len(projects)} projects with sections")
        return projects, sections_by_project


class TaskGenerator:
    """
    Generates realistic task data with proper distributions.
    Methodology: Based on Asana research and real-world usage patterns.
    """

    TASK_TEMPLATES = {
        "engineering": [
            "[Asana Platform] {action} {feature}",
            "Build {feature} for {module}",
            "Debug {issue} in {component}",
            "Refactor {component} for {goal}",
            "Add {feature} to {module}",
            "Optimize {component} performance",
            "Write tests for {module}",
            "[API] Implement {endpoint}",
            "[Database] {action} {schema_change}",
            "[Frontend] Update {component} styling",
        ],
        "marketing": [
            "[Campaign] Create {deliverable}",
            "Develop {asset_type} for {campaign}",
            "Write {content_type} about {topic}",
            "Design {asset} for {channel}",
            "[Content] Publish {content_type} on {platform}",
            "Execute {campaign_type} campaign",
            "Analyze {metric} performance",
            "[Email] Build nurture sequence",
        ],
        "operations": [
            "[Process] Implement {process}",
            "Audit {system} - {scope}",
            "Migrate {system} to {platform}",
            "Configure {tool} for {purpose}",
            "[Hiring] Recruit for {role}",
            "[Finance] Process {transaction_type}",
            "[HR] Onboard {resource}",
            "[Infrastructure] Setup {infrastructure}",
        ],
    }

    ACTIONS = ["Implement", "Fix", "Refactor", "Optimize", "Test", "Review", "Deploy", "Debug", "Build", "Write"]
    DETAILS = ["performance", "reliability", "security", "user experience", "scalability", "accessibility"]
    DELIVERABLES = ["copy", "design", "video", "infographic", "case study", "whitepaper", "webinar"]

    @classmethod
    def generate_tasks(
        cls,
        project_id: str,
        section_ids: List[str],
        user_ids: List[str],
        created_by: str,
        count: int = 50,
        created_after: datetime = None
    ) -> List[Dict]:
        """
        Generate realistic task data.
        
        Args:
            project_id: Project ID
            section_ids: List of section IDs in project
            user_ids: List of user IDs for assignment
            created_by: User ID of creator
            count: Number of tasks
            created_after: Start date for task creation
            
        Returns:
            List of task dictionaries
        """
        if created_after is None:
            created_after = datetime.utcnow() - timedelta(days=90)
        
        tasks = []
        
        # Additional context for realistic task names
        COMPONENTS = ["Auth", "API", "Database", "UI", "Cache", "Frontend", "Backend", "Mobile"]
        FEATURES = ["notifications", "search", "filtering", "export", "goals", "timeline", "portfolio", "ai_features"]
        MODULES = ["Core", "Integration", "Admin", "Dashboard", "Platform", "Services"]
        ISSUES = ["race condition", "memory leak", "timeout", "validation error", "performance", "security"]
        ROLES = ["Senior Engineer", "Product Manager", "Designer", "QA Engineer"]
        ENDPOINTS = ["/api/tasks", "/api/goals", "/api/projects", "/api/portfolios", "/api/users"]
        
        for i in range(count):
            task_id = str(uuid.uuid4())
            
            # Task creation date within project timeline
            days_offset = random.randint(0, 90)
            created_at = created_after + timedelta(days=days_offset)
            
            # Task name generation with flexible templating
            if random.random() < 0.7:
                template = random.choice(cls.TASK_TEMPLATES["engineering"])
                try:
                    name = template.format(
                        component=random.choice(COMPONENTS),
                        action=random.choice(cls.ACTIONS),
                        detail=random.choice(cls.DETAILS),
                        feature=random.choice(FEATURES),
                        module=random.choice(MODULES),
                        issue=random.choice(ISSUES),
                        goal=random.choice(["better performance", "maintainability", "readability"]),
                        endpoint=random.choice(ENDPOINTS),
                        schema_change=random.choice(["migration", "optimization", "normalization"]),
                    )
                except (KeyError, IndexError):
                    name = f"Task {i+1}: {random.choice(['Feature', 'Bug', 'Improvement'])} Request"
            else:
                name = f"Task {i+1}: {random.choice(['Feature', 'Bug', 'Improvement'])} Request"
            
            # Due date distribution
            due_date = cls._generate_due_date(created_at)
            
            # Task priority
            priority = random.choices(
                ["low", "medium", "high", "urgent"],
                weights=[0.35, 0.40, 0.20, 0.05]
            )[0]
            
            # Completion
            completed = random.random() < 0.65
            completed_at = None
            if completed:
                days_to_complete = max(1, int(random.lognormvariate(1.5, 0.8)))
                completed_at = created_at + timedelta(days=min(days_to_complete, 14))
            
            # Assignment
            assigned_to = random.choice(user_ids) if random.random() < 0.85 else None
            
            task = {
                "task_id": task_id,
                "project_id": project_id,
                "section_id": random.choice(section_ids),
                "name": name,
                "description": cls._generate_task_description(name),
                "created_at": created_at.isoformat(),
                "updated_at": (created_at + timedelta(hours=random.randint(1, 48))).isoformat(),
                "created_by": created_by,
                "assigned_to": assigned_to,
                "due_date": due_date.isoformat() if due_date else None,
                "start_date": (created_at.date()).isoformat() if random.random() < 0.3 else None,
                "completed": completed,
                "completed_at": completed_at.isoformat() if completed_at else None,
                "priority": priority,
                "effort_estimate": random.choice([None, 1, 2, 3, 5, 8, 13]) if random.random() < 0.4 else None,
                "effort_spent": 0,
                "status": "completed" if completed else random.choice(["not_started", "in_progress", "in_review"]),
                "parent_task_id": None,
                "display_order": i,
            }
            tasks.append(task)
        
        logger.info(f"Generated {len(tasks)} tasks for project {project_id}")
        return tasks

    @staticmethod
    def _generate_due_date(created_at: datetime) -> Optional[date]:
        """
        Generate due date following realistic distribution.
        Distribution: 25% within 1 week, 40% within 1 month, 20% 1-3 months,
                     10% no due date
        """
        rand = random.random()
        
        if rand < 0.25:
            days = random.randint(1, 7)
        elif rand < 0.65:
            days = random.randint(8, 30)
        elif rand < 0.85:
            days = random.randint(31, 90)
        else:
            return None
        
        due_date = created_at + timedelta(days=days)
        
        # Avoid weekends for 85% of tasks
        if random.random() < 0.85:
            while due_date.weekday() in [5, 6]:
                due_date += timedelta(days=1)
        
        return due_date.date()

    @staticmethod
    def _generate_task_description(task_name: str) -> Optional[str]:
        """Generate task description with proper distribution.
        Uses LLM enhancement if available, falls back to templates."""
        rand = random.random()
        
        if rand < 0.20:
            return None  # 20% no description
        elif rand < 0.70:
            # 50% short description - try LLM first
            llm_desc = enhance_task_description(task_name, "general")
            if llm_desc:
                return llm_desc
            
            # Fallback templates
            descriptions = [
                f"Please complete: {task_name.lower()}",
                f"Working on: {task_name.lower()}",
                f"Task to handle: {task_name.lower()}",
                "See related tasks for more context.",
            ]
            return random.choice(descriptions)
        else:
            # 30% detailed description
            return f"""
## Overview
{task_name}

## Details
- This task is important for the project
- Please review related documentation
- Follow the coding standards

## Acceptance Criteria
- [ ] Implementation complete
- [ ] Tests written and passing
- [ ] Code reviewed
- [ ] Deployed to staging

## References
See wiki and related tasks for more information.
"""


class CommentGenerator:
    """Generates realistic comments on tasks."""

    COMMENT_TEMPLATES = [
        "Just reviewed this - looks good! Have a few minor comments.",
        "Blocked on {dependency}. Let me know when it's ready.",
        "Assigned this to {assignee}. Please start when you get a chance.",
        "This is ready for review. Please take a look.",
        "Deployed to production. Monitoring for any issues.",
        "All tests passing. Ready to merge.",
        "Found a few edge cases we should handle.",
        "Updated based on feedback. Ready for next review.",
    ]

    @classmethod
    def generate_comments(
        cls,
        task_id: str,
        created_by: str,
        user_ids: List[str],
        task_created_at: datetime,
        task_completed_at: Optional[datetime] = None,
        task_name: Optional[str] = None
    ) -> List[Dict]:
        """Generate realistic comments on a task with optional LLM enhancement."""
        comments = []
        
        # 50% of tasks have comments
        if random.random() > 0.5:
            return comments
        
        num_comments = random.randint(1, 5)
        end_time = task_completed_at if task_completed_at else datetime.utcnow()
        
        for i in range(num_comments):
            # Comments spread over task lifecycle
            days_offset = random.randint(0, int((end_time - task_created_at).days))
            comment_time = task_created_at + timedelta(days=days_offset, hours=random.randint(0, 23))
            
            # Try LLM enhancement for more realistic comments
            commenter_id = random.choice(user_ids)
            roles = ["Engineer", "Manager", "Designer", "QA", "DevOps"]
            role = random.choice(roles)
            
            llm_content = None
            if task_name and random.random() < 0.3:  # 30% chance to use LLM
                llm_content = enhance_comment(task_name, role)
            
            content = llm_content if llm_content else random.choice(cls.COMMENT_TEMPLATES)
            
            comment = {
                "comment_id": str(uuid.uuid4()),
                "task_id": task_id,
                "author_id": commenter_id,
                "content": content,
                "created_at": comment_time.isoformat(),
                "updated_at": comment_time.isoformat(),
                "is_pinned": False,
                "comment_type": "comment",
            }
            comments.append(comment)
        
        return comments


class TagGenerator:
    """Generates realistic tags."""

    COMMON_TAGS = [
        "urgent", "bug", "feature", "documentation", "refactor",
        "performance", "security", "ui/ux", "backend", "frontend",
        "database", "api", "testing", "review", "blocked",
        "in-progress", "help-wanted", "good-first-issue"
    ]

    COLORS = [
        "#FF0000", "#FFA500", "#FFFF00", "#00FF00", "#0000FF",
        "#4B0082", "#9400D3", "#FF1493", "#00CED1", "#90EE90"
    ]

    @classmethod
    def generate_tags(
        cls,
        organization_id: str,
        created_by: str,
        count: int = 15
    ) -> List[Dict]:
        """Generate realistic tags."""
        tags = []
        selected_tags = random.sample(cls.COMMON_TAGS, min(count, len(cls.COMMON_TAGS)))
        
        for tag_name in selected_tags:
            tag = {
                "tag_id": str(uuid.uuid4()),
                "organization_id": organization_id,
                "name": tag_name,
                "color": random.choice(cls.COLORS),
                "created_at": (datetime.utcnow() - timedelta(days=random.randint(1, 90))).isoformat(),
                "created_by": created_by,
            }
            tags.append(tag)
        
        return tags
