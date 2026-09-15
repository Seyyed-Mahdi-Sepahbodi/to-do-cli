"""
Unit tests for domain entity and business rules.
"""
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from task_cli.domain.enums import TaskPriority, TaskStatus
from task_cli.domain.exceptions import InvalidTaskDataError
from task_cli.domain.models import Task

def test_create_task_with_default_values():
    task = Task(title="Buy Groceries")
    assert task.title == "Buy Groceries"
    assert task.status == TaskStatus.TODO
    assert task.priority == TaskPriority.MEDIUM
    assert task.description == ""
    assert task.tags == []
    assert task.deadline is None
    assert len(task.id) == 8
    assert isinstance(task.created_at, datetime)

def test_task_empty_title_raises_error():
    with pytest.raises((InvalidTaskDataError, ValidationError)):
        Task(title="   ")

def test_task_status_transitions():
    task = Task(title="Develop Feature")
    original_updated_at = task.updated_at

    task.mark_as_in_progress()
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.updated_at >= original_updated_at

    task.mark_as_done()
    assert task.status == TaskStatus.DONE

def test_task_update_details():
    task = Task(title="Initial Title", priority=TaskPriority.LOW)
    task.update_details(
        title="Updated Title",
        priority=TaskPriority.HIGH,
        tags=["python", "cli"],
    )

    assert task.title == "Updated Title"
    assert task.priority == TaskPriority.HIGH
    assert task.tags == ["python", "cli"]

def test_task_update_with_empty_title_raises_error():
    task = Task(title="Valid Title")
    with pytest.raises(InvalidTaskDataError):
        task.update_details(title="   ")
