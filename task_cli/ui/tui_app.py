"""
Main textual TUI application for task CLI.
"""
from datetime import datetime
from typing import Optional
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import DataTable, Footer, Header, Label, Static

from task_cli.domain.enums import TaskPriority, TaskStatus
from task_cli.infrastructure.config import StorageType, get_repository
from task_cli.services.task_service import TaskService
from task_cli.ui.tui_modals import AddTaskModal


class StatsWidget(Static):
    """Widget displaying dashboard metrics."""

    def update_stats(self, stats: dict) -> None:
        text = (
            f"[b]Total:[/b] {stats['total']}  |  "
            f"[cyan][b]Todo:[/b] {stats['todo']}[/]  |  "
            f"[yellow][b]In Progress:[/b] {stats['in_progress']}[/]  |  "
            f"[green][b]Done:[/b] {stats['done']}[/]  |  "
            f"[red][b]Overdue:[/b] {stats['overdue']}[/]"
        )
        self.update(text)


class TaskManagerTUI(App[None]):
    """Modern Interactive Terminal Task Manager."""

    TITLE = "⚡ TaskFlow TUI Manager"
    SUB_TITLE = "Mouse & Keyboard Friendly Terminal Dashboard"
    CSS = """
    Screen {
        layout: vertical;
    }

    #stats-bar {
        dock: top;
        height: 3;
        background: $panel;
        color: $text;
        content-align: center middle;
        border-bottom: solid $accent;
    }

    #main-container {
        height: 1fr;
        padding: 1;
    }

    DataTable {
        height: 1fr;
        border: round $primary;
    }

    DataTable > .datatable--cursor {
        background: $accent 30%;
        color: $text;
    }
    """

    BINDINGS = [
        Binding("a", "add_task", "Add Task", priority=True),
        Binding("space", "toggle_status", "Cycle Status", priority=True),
        Binding("d", "delete_task", "Delete", priority=True),
        Binding("r", "refresh_data", "Refresh"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, storage_type: StorageType = StorageType.SQLITE):
        super().__init__()
        self.service = TaskService(repository=get_repository(storage_type))

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield StatsWidget(id="stats-bar")
        with Container(id="main-container"):
            yield DataTable(cursor_type="row", id="tasks-table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Status", "Priority", "Title", "Deadline", "Tags")
        self.reload_tasks()

    def reload_tasks(self) -> None:
        """Fetch tasks and refresh DataTable and Stats widget."""
        table = self.query_one(DataTable)
        stats_widget = self.query_one(StatsWidget)

        # Update stats
        stats = self.service.get_statistics()
        stats_widget.update_stats(stats)

        # Update table rows
        table.clear()
        tasks = self.service.list_tasks()

        for task in tasks:
            status_style = {
                TaskStatus.DONE: "[green]✔ DONE[/green]",
                TaskStatus.IN_PROGRESS: "[cyan]⏳ IN_PROGRESS[/cyan]",
                TaskStatus.TODO: "[dim white]⏹ TODO[/dim white]",
            }.get(task.status, task.status.value)

            prio_style = {
                TaskPriority.CRITICAL: "[bold red]CRITICAL[/bold red]",
                TaskPriority.HIGH: "[red]HIGH[/red]",
                TaskPriority.MEDIUM: "[yellow]MEDIUM[/yellow]",
                TaskPriority.LOW: "[blue]LOW[/blue]",
            }.get(task.priority, task.priority.value)

            dl_str = task.deadline.strftime("%Y-%m-%d") if task.deadline else "-"
            tags_str = ", ".join(task.tags) if task.tags else "-"

            table.add_row(
                task.id,
                status_style,
                prio_style,
                task.title,
                dl_str,
                tags_str,
                key=task.id,
            )

    def action_add_task(self) -> None:
        """Open modal to add a new task."""
        def handle_modal_result(result: Optional[dict]) -> None:
            if result:
                parsed_dl = datetime.fromisoformat(result["deadline"]) if result["deadline"] else None
                self.service.create_task(
                    title=result["title"],
                    priority=TaskPriority(result["priority"]),
                    tags=result["tags"],
                    deadline=parsed_dl,
                )
                self.reload_tasks()
                self.notify(f"Task '{result['title']}' created successfully!")

        self.push_screen(AddTaskModal(), handle_modal_result)

    def _get_selected_task_id(self) -> Optional[str]:
        table = self.query_one(DataTable)
        if table.row_count == 0 or table.cursor_row is None:
            return None
        # In Textual DataTable, key of row is stored or retrieved via cell
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        return str(row_key.value)

    def action_toggle_status(self) -> None:
        """Cycle task status (TODO -> IN_PROGRESS -> DONE -> TODO)."""
        task_id = self._get_selected_task_id()
        if not task_id:
            self.notify("No task selected!", severity="warning")
            return

        task = self.service.get_task(task_id)
        next_status = {
            TaskStatus.TODO: TaskStatus.IN_PROGRESS,
            TaskStatus.IN_PROGRESS: TaskStatus.DONE,
            TaskStatus.DONE: TaskStatus.TODO,
        }.get(task.status, TaskStatus.TODO)

        self.service.mark_task_status(task_id, next_status)
        self.reload_tasks()
        self.notify(f"Status changed to {next_status.value}")

    def action_delete_task(self) -> None:
        """Delete currently selected task."""
        task_id = self._get_selected_task_id()
        if not task_id:
            self.notify("No task selected!", severity="warning")
            return

        self.service.delete_task(task_id)
        self.reload_tasks()
        self.notify("Task deleted successfully!", severity="information")

    def action_refresh_data(self) -> None:
        """Manual refresh."""
        self.reload_tasks()
        self.notify("Data refreshed.")
