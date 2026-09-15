"""
Automated tests for textual TUI workflows.
"""
import pytest
from task_cli.ui.tui_app import TaskManagerTUI
from textual.widgets import DataTable


@pytest.mark.asyncio
async def test_tui_initial_load_and_table(tmp_path, monkeypatch):
    test_db = tmp_path / "tui_test.db"
    monkeypatch.setattr("task_cli.infrastructure.config.DEFAULT_SQLITE_PATH", test_db)

    app = TaskManagerTUI()

    # Pre-populate a task
    app.service.create_task(title="TUI Feature Task", tags=["ui"])

    async with app.run_test() as pilot:
        # Check if table exists and loaded row
        table = app.query_one(DataTable)
        assert table.row_count == 1
        
        # Test Refresh key binding
        await pilot.press("r")
        assert table.row_count == 1

        # Test Quit
        await pilot.press("q")
