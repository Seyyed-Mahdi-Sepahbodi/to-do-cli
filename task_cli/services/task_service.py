"""
Core application service orchestrating Task business logic and use cases.
"""
from datetime import datetime, timedelta, timezone
from task_cli.domain.enums import TaskPriority, TaskStatus
from task_cli.domain.exceptions import TaskNotFoundError
from task_cli.domain.models import Task
from task_cli.ports.repository import TaskRepository


class TaskService:
    """Service handling task business use cases."""

    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        tags: list[str] | None = None,
        deadline: datetime | None = None,
    ) -> Task:
        """Creates and stores a new task."""
        task = Task(
            title=title,
            description=description,
            priority=priority,
            tags=tags or [],
            deadline=deadline,
        )
        return self._repository.save(task)

    def get_task(self, task_id: str) -> Task:
        """Retrieves a single task by ID or raises TaskNotFoundError."""
        task = self._repository.get_by_id(task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        return task

    def list_tasks(
        self,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        tag: str | None = None,
        search_query: str | None = None,
        is_overdue: bool | None = None,
    ) -> list[Task]:
        """Retrieves tasks with comprehensive filtering and searching."""
        tasks = self._repository.get_all()
        now = datetime.now(timezone.utc)

        filtered_tasks: list[Task] = []
        for task in tasks:
            if status is not None and task.status != status:
                continue

            if priority is not None and task.priority != priority:
                continue

            if tag is not None and tag.lower() not in [t.lower() for t in task.tags]:
                continue

            if search_query is not None:
                query = search_query.lower()
                matches_title = query in task.title.lower()
                matches_desc = query in task.description.lower()
                if not (matches_title or matches_desc):
                    continue

            if is_overdue is not None:
                if is_overdue:
                    # Task is overdue if it has a deadline in the past and is not DONE
                    if not (task.deadline and task.deadline < now and task.status != TaskStatus.DONE):
                        continue
                else:
                    # Not overdue
                    if task.deadline and task.deadline < now and task.status != TaskStatus.DONE:
                        continue

            filtered_tasks.append(task)

        return filtered_tasks

    def update_task(
        self,
        task_id: str,
        title: str | None = None,
        description: str | None = None,
        priority: TaskPriority | None = None,
        deadline: datetime | None = None,
        tags: list[str] | None = None,
    ) -> Task:
        """Updates task information."""
        task = self.get_task(task_id)
        task.update_details(
            title=title,
            description=description,
            priority=priority,
            deadline=deadline,
            tags=tags,
        )
        return self._repository.save(task)

    def mark_task_status(self, task_id: str, status: TaskStatus) -> Task:
        """Transitions a task status."""
        task = self.get_task(task_id)
        if status == TaskStatus.DONE:
            task.mark_as_done()
        elif status == TaskStatus.IN_PROGRESS:
            task.mark_as_in_progress()
        else:
            task.status = TaskStatus.TODO
            task.updated_at = datetime.now(timezone.utc)

        return self._repository.save(task)

    def delete_task(self, task_id: str) -> bool:
        """Deletes a task by ID."""
        # Ensure task exists first
        self.get_task(task_id)
        return self._repository.delete(task_id)

    def get_statistics(self) -> dict[str, int]:
        """Calculates high-level statistics for dashboard/reporting."""
        tasks = self._repository.get_all()
        now = datetime.now(timezone.utc)

        total = len(tasks)
        todo = sum(1 for t in tasks if t.status == TaskStatus.TODO)
        in_progress = sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS)
        done = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        overdue = sum(
            1 for t in tasks if t.deadline and t.deadline < now and t.status != TaskStatus.DONE
        )

        return {
            "total": total,
            "todo": todo,
            "in_progress": in_progress,
            "done": done,
            "overdue": overdue,
        }
