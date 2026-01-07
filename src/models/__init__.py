"""
Data models for Asana simulation database.
Uses dataclasses with validation and type hints for type safety.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum
import uuid


class TeamType(str, Enum):
    ENGINEERING = "engineering"
    MARKETING = "marketing"
    OPERATIONS = "operations"
    PRODUCT = "product"
    DESIGN = "design"
    SALES = "sales"
    FINANCE = "finance"
    HR = "hr"
    CROSS_FUNCTIONAL = "cross-functional"


class ProjectType(str, Enum):
    SPRINT = "sprint"
    ONGOING = "ongoing"
    BUG_TRACKING = "bug_tracking"
    MARKETING_CAMPAIGN = "marketing_campaign"
    OPS_INITIATIVE = "ops_initiative"


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    TEMPLATE = "template"
    COMPLETED = "completed"


class ProjectVisibility(str, Enum):
    PRIVATE = "private"
    TEAM = "team"
    PUBLIC = "public"


class TaskStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    BLOCKED = "blocked"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Organization:
    """Organization/Workspace entity."""
    organization_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    domain: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    employee_count: int = 0
    industry: Optional[str] = None
    location: Optional[str] = None
    is_verified: bool = False

    def validate(self) -> bool:
        """Validate organization data."""
        return bool(self.name and self.domain and self.organization_id)


@dataclass
class Team:
    """Team within an organization."""
    team_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str = ""
    name: str = ""
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    team_type: TeamType = TeamType.ENGINEERING

    def validate(self) -> bool:
        """Validate team data."""
        return bool(self.team_id and self.organization_id and self.name)


@dataclass
class User:
    """User in the workspace."""
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str = ""
    email: str = ""
    name: str = ""
    first_name: str = ""
    last_name: str = ""
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    is_admin: bool = False
    department: Optional[str] = None
    role: Optional[str] = None
    joined_date: Optional[datetime] = None

    def validate(self) -> bool:
        """Validate user data."""
        return bool(self.user_id and self.organization_id and self.email and self.name)


@dataclass
class TeamMember:
    """Team membership mapping."""
    team_member_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    team_id: str = ""
    user_id: str = ""
    joined_at: datetime = field(default_factory=datetime.utcnow)
    role: str = "member"
    is_active: bool = True

    def validate(self) -> bool:
        """Validate team member data."""
        return bool(self.team_id and self.user_id and self.team_member_id)


@dataclass
class Project:
    """Project entity."""
    project_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str = ""
    team_id: Optional[str] = None
    name: str = ""
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    archived_at: Optional[datetime] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: ProjectStatus = ProjectStatus.ACTIVE
    project_type: ProjectType = ProjectType.SPRINT
    visibility: ProjectVisibility = ProjectVisibility.TEAM

    def validate(self) -> bool:
        """Validate project data."""
        return bool(self.project_id and self.organization_id and self.name and self.created_by)


@dataclass
class ProjectMember:
    """Project member assignment."""
    project_member_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    user_id: str = ""
    added_at: datetime = field(default_factory=datetime.utcnow)
    role: str = "member"

    def validate(self) -> bool:
        """Validate project member data."""
        return bool(self.project_member_id and self.project_id and self.user_id)


@dataclass
class Section:
    """Section within a project."""
    section_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    name: str = ""
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    display_order: int = 0

    def validate(self) -> bool:
        """Validate section data."""
        return bool(self.section_id and self.project_id and self.name)


@dataclass
class Tag:
    """Tag/Label for tasks."""
    tag_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str = ""
    name: str = ""
    color: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""

    def validate(self) -> bool:
        """Validate tag data."""
        return bool(self.tag_id and self.organization_id and self.name and self.created_by)


@dataclass
class Task:
    """Task entity - core unit of work."""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    section_id: Optional[str] = None
    name: str = ""
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    assigned_to: Optional[str] = None
    due_date: Optional[date] = None
    start_date: Optional[date] = None
    completed: bool = False
    completed_at: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    effort_estimate: Optional[int] = None
    effort_spent: int = 0
    status: TaskStatus = TaskStatus.NOT_STARTED
    parent_task_id: Optional[str] = None
    display_order: int = 0

    def validate(self) -> bool:
        """Validate task data."""
        if not (self.task_id and self.project_id and self.name and self.created_by):
            return False
        # Ensure temporal consistency
        if self.completed_at and self.completed_at < self.created_at:
            return False
        return True


@dataclass
class TaskTag:
    """Task-Tag association."""
    task_tag_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    tag_id: str = ""
    added_at: datetime = field(default_factory=datetime.utcnow)

    def validate(self) -> bool:
        """Validate task tag data."""
        return bool(self.task_tag_id and self.task_id and self.tag_id)


@dataclass
class Comment:
    """Comment/Story on a task."""
    comment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    author_id: str = ""
    content: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_pinned: bool = False
    comment_type: str = "comment"

    def validate(self) -> bool:
        """Validate comment data."""
        return bool(self.comment_id and self.task_id and self.author_id and self.content)
