"""
CLI Presentation Layer using Typer and Rich.
"""
from datetime import datetime
import json
from typing import Annotated, Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from task_cli.domain.enums import TaskPriority, TaskStatus
from task_cli.domain.exceptions import TaskNotFoundError
from task_cli.infrastructure.config import StorageType, get_repository
from task_cli.services.task_service import TaskService

app = typer.Typer(
    name="task-cli",
    help="⚡ Modern Task Management CLI & TUI System",
    no_args_is_help=True,
)
console = Console()


def get_service(storage: StorageType = StorageType.SQLITE) -> TaskService:
    repo = get_repository(storage_type=storage)
    return TaskService(repository=repo)


def priority_color(priority: TaskPriority) -> str:
    match priority:
        case TaskPriority.CRITICAL:
            return "[bold red]"
        case TaskPriority.HIGH:
            return "[red]"
        case TaskPriority.MEDIUM:
            return "[yellow]"
        case TaskPriority.LOW:
            return "[blue]"


def status_badge(status: TaskStatus) -> str:
    match status:
        case TaskStatus.DONE:
            return "[bold green]✔ DONE[/bold green]"
        case TaskStatus.IN_PROGRESS:
            return "[bold cyan]⏳ IN_PROGRESS[/bold cyan]"
        case TaskStatus.TODO:
            return "[bold white]⏹ TODO[/bold white]"


@app.command()
def add(
    title: Annotated[str, typer.Argument(help="Title of the task")],
    description: Annotated[str, typer.Option("--desc", "-d", help="Task description")] = "",
    priority: Annotated[TaskPriority, typer.Option("--priority", "-p", help="Priority level")] = TaskPriority.MEDIUM,
    tags: Annotated[Optional[list[str]], typer.Option("--tag", "-t", help="Tags for categorizing")] = None,
    deadline: Annotated[Optional[str], typer.Option("--deadline", help="Deadline in YYYY-MM-DD format")] = None,
    storage: Annotated[StorageType, typer.Option("--storage", "-s", help="Storage backend")] = StorageType.SQLITE,
) -> None:
    """➕ Add a new task to your list."""
    service = get_service(storage)
    parsed_deadline = datetime.fromisoformat(deadline) if deadline else None

    task = service.create_task(
        title=title,
        description=description,
        priority=priority,
        tags=tags or [],
        deadline=parsed_deadline,
    )
    console.print(f"[bold green]✔ Task created successfully![/bold green] (ID: [bold yellow]{task.id}[/bold yellow])")


@app.command(name="list")
def list_tasks(
    status: Annotated[Optional[TaskStatus], typer.Option("--status", help="Filter by status")] = None,
    priority: Annotated[Optional[TaskPriority], typer.Option("--priority", "-p", help="Filter by priority")] = None,
    tag: Annotated[Optional[str], typer.Option("--tag", "-t", help="Filter by tag")] = None,
    search: Annotated[Optional[str], typer.Option("--search", "-q", help="Search in title and description")] = None,
    overdue: Annotated[bool, typer.Option("--overdue", help="Show only overdue tasks")] = False,
    storage: Annotated[StorageType, typer.Option("--storage", "-s", help="Storage backend")] = StorageType.SQLITE,
) -> None:
    """📋 List tasks with interactive filtering and styling."""
    service = get_service(storage)
    tasks = service.list_tasks(
        status=status,
        priority=priority,
        tag=tag,
        search_query=search,
        is_overdue=True if overdue else None,
    )

    if not tasks:
        console.print("[dim yellow]No tasks found matching your criteria.[/dim yellow]")
        return

    table = Table(title="📑 Task Registry", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=10)
    table.add_column("Status", width=16)
    table.add_column("Priority", width=12)
    table.add_column("Title", style="bold")
    table.add_column("Deadline", style="cyan", width=14)
    table.add_column("Tags", style="green")

    for task in tasks:
        dl_str = task.deadline.strftime("%Y-%m-%d") if task.deadline else "-"
        tags_str = ", ".join(task.tags) if task.tags else "-"
        table.add_row(
            task.id,
            status_badge(task.status),
            f"{priority_color(task.priority)}{task.priority.value.upper()}[/]",
            task.title,
            dl_str,
            tags_str,
        )

    console.print(table)


@app.command()
def done(
    task_id: Annotated[str, typer.Argument(help="ID of task to complete")],
    storage: Annotated[StorageType, typer.Option("--storage", "-s", help="Storage backend")] = StorageType.SQLITE,
) -> None:
    """✔ Mark a task as completed (DONE)."""
    service = get_service(storage)
    try:
        task = service.mark_task_status(task_id, TaskStatus.DONE)
        console.print(f"[bold green]✔ Task '{task.title}' marked as DONE![/bold green]")
    except TaskNotFoundError:
        console.print(f"[bold red]✘ Error: Task with ID '{task_id}' not found.[/bold red]")


@app.command()
def delete(
    task_id: Annotated[str, typer.Argument(help="ID of task to delete")],
    storage: Annotated[StorageType, typer.Option("--storage", "-s", help="Storage backend")] = StorageType.SQLITE,
) -> None:
    """🗑 Delete a task by ID."""
    service = get_service(storage)
    try:
        service.delete_task(task_id)
        console.print(f"[bold red]✔ Task '{task_id}' deleted successfully.[/bold red]")
    except TaskNotFoundError:
        console.print(f"[bold red]✘ Error: Task with ID '{task_id}' not found.[/bold red]")


@app.command()
def stats(
    storage: Annotated[StorageType, typer.Option("--storage", "-s", help="Storage backend")] = StorageType.SQLITE,
) -> None:
    """📊 View dashboard metrics and task summaries."""
    service = get_service(storage)
    data = service.get_statistics()

    summary_text = (
        f"[bold]Total Tasks:[/bold] {data['total']}\n"
        f"[white]Todo:[/white] {data['todo']} | "
        f"[cyan]In Progress:[/cyan] {data['in_progress']} | "
        f"[green]Completed:[/green] {data['done']}\n"
        f"[red]Overdue:[/red] {data['overdue']}"
    )

    console.print(Panel(summary_text, title="📈 Task Overview Summary", expand=False, border_style="cyan"))


if __name__ == "__main__":
    app()
