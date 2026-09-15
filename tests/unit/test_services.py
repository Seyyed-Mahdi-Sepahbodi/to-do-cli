"""
Unit tests for TaskService.
"""
from datetime import datetime, timedelta, timezone
import pytest

from task_cli.domain.enums import TaskPriority, TaskStatus
from task_cli.domain.exceptions import TaskNotFoundError
from task_cli.domain.models import Task
from task_cli.infrastructure.sqlite_repo import SQLiteTaskRepository
from task_cli.services.task_service import TaskService


@pytest.fixture
def task_service(tmp_path) -> TaskService:
    repo = SQLiteTaskRepository(db_path=tmp_path / "test_service.db")
    return TaskService(repository=repo)


def test_create_and_get_task(task_service: TaskService):
    task = task_service.create_task(
        title="Write Unit Tests",
        description="Must achieve high coverage",
        priority=TaskPriority.HIGH,
        tags=["dev", "test"],
    )

    retrieved = task_service.get_task(task.id)
    assert retrieved.id == task.id
    assert retrieved.title == "Write Unit Tests"
    assert retrieved.priority == TaskPriority.HIGH


def test_get_nonexistent_task_raises_error(task_service: TaskService):
    with pytest.raises(TaskNotFoundError):
        task_service.get_task("non-existent-id")


def test_filter_and_search_tasks(task_service: TaskService):
    task_service.create_task(title="Fix login bug", tags=["auth", "bug"], priority=TaskPriority.HIGH)
    task_service.create_task(title="Refactor backend", tags=["core"], priority=TaskPriority.MEDIUM)
    task_service.create_task(title="Design UI dashboard", tags=["ui"], priority=TaskPriority.LOW)

    # Filter by Priority
    high_tasks = task_service.list_tasks(priority=TaskPriority.HIGH)
    assert len(high_tasks) == 1
    assert high_tasks[0].title == "Fix login bug"

    # Filter by Tag
    core_tasks = task_service.list_tasks(tag="core")
    assert len(core_tasks) == 1
    assert core_tasks[0].title == "Refactor backend"

    # Search by text
    search_results = task_service.list_tasks(search_query="login")
    assert len(search_results) == 1
    assert search_results[0].title == "Fix login bug"


def test_overdue_tasks_filter(task_service: TaskService):
    now = datetime.now(timezone.utc)
    past_date = now - timedelta(days=2)
    future_date = now + timedelta(days=2)

    task_service.create_task(title="Overdue task", deadline=past_date)
    task_service.create_task(title="Future task", deadline=future_date)
    completed_past = task_service.create_task(title="Done overdue task", deadline=past_date)
    task_service.mark_task_status(completed_past.id, TaskStatus.DONE)

    overdue_tasks = task_service.list_tasks(is_overdue=True)
    assert len(overdue_tasks) == 1
    assert overdue_tasks[0].title == "Overdue task"


def test_task_statistics(task_service: TaskService):
    now = datetime.now(timezone.utc)
    past_date = now - timedelta(days=1)

    t1 = task_service.create_task(title="Task 1", deadline=past_date)
    t2 = task_service.create_task(title="Task 2")
    t3 = task_service.create_task(title="Task 3")

    task_service.mark_task_status(t2.id, TaskStatus.IN_PROGRESS)
    task_service.mark_task_status(t3.id, TaskStatus.DONE)

    stats = task_service.get_statistics()
    assert stats["total"] == 3
    assert stats["todo"] == 1
    assert stats["in_progress"] == 1
    assert stats["done"] == 1
    assert stats["overdue"] == 1
