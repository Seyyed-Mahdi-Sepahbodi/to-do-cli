"""
Integration tests for CLI interactions using CliRunner.
"""
from typer.testing import CliRunner
from task_cli.ui.cli import app
from task_cli.infrastructure.sqlite_repo import SQLiteTaskRepository
from task_cli.services.task_service import TaskService
import pytest

runner = CliRunner()


def test_cli_add_and_list_flow(tmp_path, monkeypatch):
    test_db = tmp_path / "cli_test.db"
    # Override default db for testing
    monkeypatch.setattr("task_cli.infrastructure.config.DEFAULT_SQLITE_PATH", test_db)

    # 1. Add Task
    result = runner.invoke(app, ["add", "Write CLI Documentation", "--priority", "high", "-t", "docs"])
    assert result.exit_code == 0
    assert "Task created successfully!" in result.stdout

    # 2. List Tasks
    list_result = runner.invoke(app, ["list"])
    assert list_result.exit_code == 0
    assert "Write CLI Documentation" in list_result.stdout
    assert "HIGH" in list_result.stdout


def test_cli_mark_done_and_stats(tmp_path, monkeypatch):
    test_db = tmp_path / "cli_test2.db"
    monkeypatch.setattr("task_cli.infrastructure.config.DEFAULT_SQLITE_PATH", test_db)

    # Setup task directly
    repo = SQLiteTaskRepository(db_path=test_db)
    service = TaskService(repository=repo)
    task = service.create_task(title="Fix integration test")

    # Mark as Done via CLI
    done_result = runner.invoke(app, ["done", task.id])
    assert done_result.exit_code == 0
    assert "marked as DONE!" in done_result.stdout

    # Check Stats
    stats_result = runner.invoke(app, ["stats"])
    assert stats_result.exit_code == 0
    assert "Completed: 1" in stats_result.stdout
