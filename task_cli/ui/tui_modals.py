"""
Modal dialogs for the textual TUI interface.
"""
from typing import Optional
from textual.app import ComposeResult
from textual.containers import Grid, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select

from task_cli.domain.enums import TaskPriority


class AddTaskModal(ModalScreen[Optional[dict]]):
    """Modal screen for capturing new task details."""

    CSS = """
    AddTaskModal {
        align: center middle;
    }

    #dialog {
        grid-size: 2;
        grid-gutter: 1 2;
        grid-rows: auto auto auto auto 3;
        padding: 1 2;
        width: 60;
        height: auto;
        border: thick $accent;
        background: $surface;
    }

    .label {
        height: 3;
        content-align: left middle;
        text-style: bold;
    }

    #buttons-container {
        column-span: 2;
        align: right middle;
    }

    Button {
        margin-left: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Grid(id="dialog"):
            yield Label("Title:", classes="label")
            yield Input(placeholder="Task title (required)", id="task-title")

            yield Label("Priority:", classes="label")
            yield Select(
                options=[(p.name, p.value) for p in TaskPriority],
                value=TaskPriority.MEDIUM.value,
                id="task-priority",
            )

            yield Label("Tags:", classes="label")
            yield Input(placeholder="comma-separated tags (e.g. backend, urgent)", id="task-tags")

            yield Label("Deadline:", classes="label")
            yield Input(placeholder="YYYY-MM-DD (optional)", id="task-deadline")

            with Horizontal(id="buttons-container"):
                yield Button("Cancel", variant="error", id="btn-cancel")
                yield Button("Create", variant="success", id="btn-create")

    def on_mount(self) -> None:
        self.query_one("#task-title", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-create":
            title = self.query_one("#task-title", Input).value.strip()
            if not title:
                self.notify("Title cannot be empty!", severity="warning")
                return

            priority_val = self.query_one("#task-priority", Select).value
            tags_raw = self.query_one("#task-tags", Input).value.strip()
            tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []
            deadline_val = self.query_one("#task-deadline", Input).value.strip() or None

            payload = {
                "title": title,
                "priority": priority_val,
                "tags": tags,
                "deadline": deadline_val,
            }
            self.dismiss(payload)
