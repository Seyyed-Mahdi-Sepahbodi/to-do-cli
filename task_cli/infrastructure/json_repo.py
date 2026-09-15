"""
JSON file implementation of TaskRepository.
"""
import json
from pathlib import Path
from task_cli.domain.models import Task
from task_cli.ports.repository import TaskRepository

class JsonTaskRepository(TaskRepository):
    """Persists tasks inside a local JSON file."""

    def __init__(self, file_path: Path | str = "data/tasks.json") -> None:
        self.file_path = Path(file_path)
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _read_data(self) -> list[dict]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def _write_data(self, data: list[dict]) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def save(self, task: Task) -> Task:
        data = self._read_data()
        task_dict = task.model_dump(mode="json")

        existing_index = next((i for i, item in enumerate(data) if item["id"] == task.id), None)
        if existing_index is not None:
            data[existing_index] = task_dict
        else:
            data.append(task_dict)

        self._write_data(data)
        return task
    
    def get_by_id(self, task_id: str) -> Task | None:
        data = self._read_data()
        for item in data:
            if item["id"] == task_id:
                return Task.model_validate(item)
        return None

    def get_all(self) -> list[Task]:
        data = self._read_data()
        return [Task.model_validate(item) for item in data]

    def delete(self, task_id: str) -> bool:
        data = self._read_data()
        initial_length = len(data)
        data = [item for item in data if item["id"] != task_id]
        if len(data) < initial_length:
            self._write_data(data)
            return True
        return False
