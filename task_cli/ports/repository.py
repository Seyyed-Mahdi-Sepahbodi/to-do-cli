"""
Abstract repository port definition.
Follows the Dependency Inversion Principle (DIP).
"""
from abc import ABC, abstractmethod
from task_cli.domain.models import Task

class TaskRepository(ABC):
    """Abstract interface defining standard CRUD operations for tasks."""

    @abstractmethod
    def save(self, task: Task) -> Task:
        """Create or update a task."""
        pass

    @abstractmethod
    def get_by_id(self, task_id: str) -> Task | None:
        """Retrieve a task by its unique ID."""
        pass

    @abstractmethod
    def get_all(self) -> list[Task]:
        """Retrieve all stored tasks."""
        pass

    @abstractmethod
    def delete(self, task_id: str) -> bool:
        """Delete a task by ID. Returns True if deleted, False otherwise."""
        pass
