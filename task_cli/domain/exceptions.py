"""
Domain-specific exceptionf for taks management.
"""

class TaskDomainError(Exception):
    """Base exception for all domain-related errors."""
    pass


class TaskNotFoundError(TaskDomainError):
    """Raised when a requested task does not exit."""
    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        super().__init__(f"Task with ID '{task_id}' was not found.")


class InvalidTaskDataError(TaskDomainError):
    """Raised when task data fails domain business rules validation."""
    pass
