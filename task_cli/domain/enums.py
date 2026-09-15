"""
Domain enums for task management system.
Defines the valid lifecycle states and priority levels for tasks.
"""
from enum import StrEnum

class TaskStatus(StrEnum):
    """Represents the possible states of a task."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(StrEnum):
    """Represents the urgency/priority level of a task"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
