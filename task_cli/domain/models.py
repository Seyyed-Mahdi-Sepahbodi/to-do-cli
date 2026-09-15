"""
Domain entity representing a task.
"""
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field, field_validator

from task_cli.domain.enums import TaskPriority, TaskStatus
from task_cli.domain.exceptions import InvalidTaskDataError


class Task(BaseModel):
    """
    Task entity representing a unit of work.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = Field(..., min_length=1, max_length=200, description="Task summary/title")
    description: str = Field(default="", max_length=200, description="Detailed explanation of the task.")
    status: TaskStatus = Field(default=TaskStatus.TODO)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    tags: list[str] = Field(default_factory=list)
    deadline: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("title")
    @classmethod
    def validate_title_not_whitespace(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise InvalidTaskDataError("Task title cannot be empty or only whitespace.")
        return cleaned
    
    def mark_as_done(self) -> None:
        self.status = TaskStatus.DONE
        self.updated_at = datetime.now(timezone.utc)

    def mark_as_in_progress(self) -> None:
        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.now(timezone.utc)

    def update_details(
        self,
        title: str | None = None,
        description: str | None = None,
        priority: TaskPriority | None = None,
        deadline: datetime | None = None,
        tags: list[str] | None = None,
    ) -> None:
        if title is not None:
            cleaned = title.strip()
            if not cleaned:
                raise InvalidTaskDataError("Updated title cannot be empty.")
            self.title = cleaned
        
        if description is not None:
            self.description = description

        if priority is not None:
            self.priority = priority

        if deadline is not None:
            self.deadline = deadline

        if tags is not None:
            self.tags = tags
        
        self.updated_at = datetime.now(timezone.utc)
