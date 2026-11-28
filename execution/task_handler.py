"""Handle an incoming TASK_SUBMIT protocol message."""

import uuid
from typing import Any, Dict, Optional

from .task_codec import decode_task, encode_result, sign_payload, verify_payload
from .task_executor import execute_task, TaskExecutionError
from .task_results import TaskResultTracker


def _message(sender_id: str, message_type: str, payload: Dict[str, Any]) -> dict:
    return {
        "message_id": str(uuid.uuid4()),
        "sender_id": sender_id,
        "message_type": message_type,
        "payload": payload,
    }


def _error_response(
    task_id: str,
    error_type: str,
    error_message: str,
    secret: str,
    receiver_id: str,
) -> dict:
    payload = {
        "task_id": task_id,
        "status": "FAILED",
        "error_type": error_type,
        "error_message": error_message,
    }
    payload["signature"] = sign_payload(payload, secret)
    return _message(receiver_id, "TASK_ERROR", payload)


def _public_error_details(error: Exception) -> tuple:
    """Expose the original task exception when execute_task wrapped it."""
    if isinstance(error, TaskExecutionError) and error.__cause__ is not None:
        cause = error.__cause__
        return type(cause).__name__, str(cause)
    return type(error).__name__, str(error)


def handle_task_message(
    message: dict,
    shared_secret: str,
    receiver_id: str = "meshweaver-worker",
    result_tracker: Optional[TaskResultTracker] = None,
) -> dict:
    """Authenticate, execute, track and respond to a TASK_SUBMIT message.

    HMAC verification happens before cloudpickle deserialization. When a
    result tracker is supplied, the task lifecycle is recorded locally.
    """
    task_id = "unknown"
    registered = False
    try:
        if not isinstance(message, dict):
            raise ValueError("Message must be a dictionary.")
        if message.get("message_type") != "TASK_SUBMIT":
            raise ValueError("Unsupported message type; expected TASK_SUBMIT.")
        payload = message.get("payload")
        if not isinstance(payload, dict):
            raise ValueError("Message payload must be a dictionary.")
        task_id = payload.get("task_id", "unknown")
        if not isinstance(task_id, str) or not task_id:
            raise ValueError("Task ID must be a non-empty string.")
        if not verify_payload(payload, shared_secret):
            raise PermissionError("Task payload authentication failed.")

        if result_tracker is not None:
            result_tracker.submit(task_id)
            registered = True
            result_tracker.mark_running(task_id)

        # Never deserialize a task until its HMAC has been verified.
        function, args, kwargs = decode_task(payload.get("task_data"))
        result = execute_task(function, args, kwargs)
        result_data = encode_result(result)

        response_payload = {
            "task_id": task_id,
            "status": "SUCCESS",
            "result_data": result_data,
        }
        response_payload["signature"] = sign_payload(response_payload, shared_secret)

        if result_tracker is not None:
            result_tracker.mark_success(task_id, result_data)

        return _message(receiver_id, "TASK_RESULT", response_payload)

    except Exception as error:
        error_type, error_message = _public_error_details(error)
        if result_tracker is not None and registered:
            try:
                current = result_tracker.get(task_id)
                if current["status"] in {"SUBMITTED", "RUNNING"}:
                    result_tracker.mark_failed(task_id, error_type, error_message)
            except Exception:
                # Preserve the protocol error response even if tracking fails.
                pass
        return _error_response(
            task_id,
            error_type,
            error_message,
            shared_secret,
            receiver_id,
        )
