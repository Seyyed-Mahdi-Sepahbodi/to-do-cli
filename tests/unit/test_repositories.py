"""
Unit tests for JSON and SQLite Task Repositories.
"""
from datetime import datetime, timezone
import pytest

from task_cli.domain.enums import TaskPriority, TaskStatus
from task_cli.domain.models import Task
from task_cli.infrastructure.json_repo import JsonTaskRepository
from task_cli.infrastructure.sqlite_repo import SQLiteTaskRepository

@pytest.fixture(params=["json", "sqlite"])
def repository(request, tmp_path):
    """Parameterized fixture to run identical tests on both repositories."""
    if request.param == "json":
        repo_file = tmp_path / "tasks.json"
        return JsonTaskRepository(file_path=repo_file)
    else:
        db_file = tmp_path / "tasks.db"
        return SQLiteTaskRepository(db_path=db_file)

def test_save_and_get_task(repository):
    task = Task(
        title="Integration Test Task",
        description="Verify saving logic",
        priority=TaskPriority.HIGH,
        tags=["pytest", "unit"],
        deadline=datetime.now(timezone.utc),
    )

    repository.save(task)
    retrieved = repository.get_by_id(task.id)

    assert retrieved is not None
    assert retrieved.id == task.id
    assert retrieved.title == "Integration Test Task"
    assert retrieved.priority == TaskPriority.HIGH
    assert retrieved.tags == ["pytest", "unit"]
    assert retrieved.deadline is not None

def test_update_existing_task(repository):
    task = Task(title="Original Task")
    repository.save(task)

    task.update_details(title="Modified Task", priority=TaskPriority.CRITICAL)
    task.mark_as_done()
    repository.save(task)

    updated = repository.get_by_id(task.id)
    assert updated is not None
    assert updated.title == "Modified Task"
    assert updated.priority == TaskPriority.CRITICAL
    assert updated.status == TaskStatus.DONE

def test_get_all_tasks(repository):
    task1 = Task(title="Task 1")
    task2 = Task(title="Task 2")

    repository.save(task1)
    repository.save(task2)

    all_tasks = repository.get_all()
    assert len(all_tasks) == 2
    ids = {t.id for t in all_tasks}
    assert task1.id in ids
    assert task2.id in ids

def test_delete_task(repository):
    task = Task(title="Task to Delete")
    repository.save(task)

    delete_result = repository.delete(task.id)
    assert delete_result is True

    retrieved = repository.get_by_id(task.id)
    assert retrieved is None

    # Deleting again should return False
    assert repository.delete(task.id) is False
