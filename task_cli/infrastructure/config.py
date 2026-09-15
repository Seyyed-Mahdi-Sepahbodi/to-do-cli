"""
Application configuration and factory for repository instances.
"""
from enum import StrEnum
import os
from pathlib import Path

from task_cli.infrastructure.json_repo import JsonTaskRepository
from task_cli.infrastructure.sqlite_repo import SQLiteTaskRepository
from task_cli.ports.repository import TaskRepository

class StorageType(StrEnum):
    SQLITE = "sqlite"
    JSON = "json"

# Default storage directory in user home or local app data
APP_DIR = Path.home() / ".task_cli"
APP_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_SQLITE_PATH = APP_DIR / "tasks.db"
DEFAULT_JSON_PATH = APP_DIR / "tasks.json"

def get_repository(storage_type: StorageType = StorageType.SQLITE) -> TaskRepository:
    """Factory function to instantiate the selected repository."""
    # Check for override via environment variable
    env_storage = os.getenv("TASK_STORAGE_TYPE")
    selected_type = StorageType(env_storage) if env_storage in [e.value for e in StorageType] else storage_type

    if selected_type == StorageType.JSON:
        return JsonTaskRepository(file_path=DEFAULT_JSON_PATH)
    return SQLiteTaskRepository(db_path=DEFAULT_SQLITE_PATH)
