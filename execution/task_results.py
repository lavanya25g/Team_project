"""Track task lifecycle and retain bounded execution results."""

from collections import OrderedDict
from datetime import datetime, timezone
from enum import Enum
from threading import RLock
from typing import Any, Dict, List


class TaskStatus(str, Enum):
    """Lifecycle states reported by a MeshWeaver worker."""

    SUBMITTED = "SUBMITTED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class TaskStateError(RuntimeError):
    """Raised when a task status transition is invalid."""


class TaskResultTracker:
    """Thread-safe, in-memory task status and result registry.

    Completed records are evicted oldest-first when the configured capacity
    is reached. Active tasks are never evicted.
    """

    _TERMINAL_STATES = {TaskStatus.SUCCESS.value, TaskStatus.FAILED.value}

    def __init__(self, max_records: int = 1000) -> None:
        if (
            isinstance(max_records, bool)
            or not isinstance(max_records, int)
            or max_records < 1
        ):
            raise ValueError("max_records must be a positive integer.")
        self.max_records = max_records
        self._records = OrderedDict()
        self._lock = RLock()

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

    @staticmethod
    def _validate_task_id(task_id: str) -> None:
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError("task_id must be a non-empty string.")

    def _make_room(self) -> None:
        while len(self._records) >= self.max_records:
            completed_id = next(
                (
                    task_id
                    for task_id, record in self._records.items()
                    if record["status"] in self._TERMINAL_STATES
                ),
                None,
            )
            if completed_id is None:
                raise TaskStateError(
                    "Task result registry is full; no completed record can be evicted."
                )
            del self._records[completed_id]

    def submit(self, task_id: str) -> Dict[str, Any]:
        """Register a newly accepted task in SUBMITTED state."""
        self._validate_task_id(task_id)
        with self._lock:
            if task_id in self._records:
                raise TaskStateError(f"Task {task_id!r} is already registered.")
            self._make_room()
            record = {
                "task_id": task_id,
                "status": TaskStatus.SUBMITTED.value,
                "submitted_at": self._timestamp(),
                "started_at": None,
                "completed_at": None,
                "result_data": None,
                "error_type": None,
                "error_message": None,
            }
            self._records[task_id] = record
            return dict(record)

    def mark_running(self, task_id: str) -> Dict[str, Any]:
        """Move a task from SUBMITTED to RUNNING."""
        with self._lock:
            record = self._require(task_id)
            if record["status"] != TaskStatus.SUBMITTED.value:
                raise TaskStateError("Only a SUBMITTED task can become RUNNING.")
            record["status"] = TaskStatus.RUNNING.value
            record["started_at"] = self._timestamp()
            return dict(record)

    def mark_success(self, task_id: str, result_data: str) -> Dict[str, Any]:
        """Store an encoded result and move a RUNNING task to SUCCESS."""
        if not isinstance(result_data, str):
            raise TypeError("result_data must be a string.")
        with self._lock:
            record = self._require(task_id)
            if record["status"] != TaskStatus.RUNNING.value:
                raise TaskStateError("Only a RUNNING task can become SUCCESS.")
            record["status"] = TaskStatus.SUCCESS.value
            record["result_data"] = result_data
            record["completed_at"] = self._timestamp()
            return dict(record)

    def mark_failed(
        self, task_id: str, error_type: str, error_message: str
    ) -> Dict[str, Any]:
        """Record an execution or processing error for an active task."""
        if not isinstance(error_type, str) or not error_type:
            raise ValueError("error_type must be a non-empty string.")
        if not isinstance(error_message, str):
            raise TypeError("error_message must be a string.")
        with self._lock:
            record = self._require(task_id)
            if record["status"] not in {
                TaskStatus.SUBMITTED.value,
                TaskStatus.RUNNING.value,
            }:
                raise TaskStateError("Only an active task can become FAILED.")
            record["status"] = TaskStatus.FAILED.value
            record["error_type"] = error_type
            record["error_message"] = error_message
            record["completed_at"] = self._timestamp()
            return dict(record)

    def get(self, task_id: str) -> Dict[str, Any]:
        """Return a snapshot of one task record."""
        with self._lock:
            return dict(self._require(task_id))

    def list_records(self) -> List[Dict[str, Any]]:
        """Return snapshots of all retained records, oldest first."""
        with self._lock:
            return [dict(record) for record in self._records.values()]

    def _require(self, task_id: str) -> Dict[str, Any]:
        self._validate_task_id(task_id)
        try:
            return self._records[task_id]
        except KeyError as error:
            raise TaskStateError(f"Task {task_id!r} is not registered.") from error
