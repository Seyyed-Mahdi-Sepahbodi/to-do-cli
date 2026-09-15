"""
SQLite implementation of TaskRepository.
"""
from datetime import datetime
import json
from pathlib import Path
import sqlite3
from task_cli.domain.enums import TaskPriority, TaskStatus
from task_cli.domain.models import Task
from task_cli.ports.repository import TaskRepository


class SQLiteTaskRepository(TaskRepository):
    """Persists tasks inside a local SQLite database."""

    def __init__(self, db_path: Path | str = "data/tasks.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    tags TEXT,
                    deadline TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        tags_raw = row["tags"]
        tags = json.loads(tags_raw) if tags_raw else []
        deadline_raw = row["deadline"]
        deadline = datetime.fromisoformat(deadline_raw) if deadline_raw else None

        return Task(
            id=row["id"],
            title=row["title"],
            description=row["description"] or "",
            status=TaskStatus(row["status"]),
            priority=TaskPriority(row["priority"]),
            tags=tags,
            deadline=deadline,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def save(self, task: Task) -> Task:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO tasks (id, title, description, status, priority, tags, deadline, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    description=excluded.description,
                    status=excluded.status,
                    priority=excluded.priority,
                    tags=excluded.tags,
                    deadline=excluded.deadline,
                    updated_at=excluded.updated_at
                """,
                (
                    task.id,
                    task.title,
                    task.description,
                    task.status.value,
                    task.priority.value,
                    json.dumps(task.tags),
                    task.deadline.isoformat() if task.deadline else None,
                    task.created_at.isoformat(),
                    task.updated_at.isoformat(),
                ),
            )
            conn.commit()
        return task

    def get_by_id(self, task_id: str) -> Task | None:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_task(row)
        return None

    def get_all(self) -> list[Task]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [self._row_to_task(row) for row in rows]

    def delete(self, task_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0    
