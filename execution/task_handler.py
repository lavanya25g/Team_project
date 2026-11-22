"""Handle an incoming TASK_SUBMIT protocol message."""

import uuid
from typing import Any, Dict

from .task_codec import (
    TaskPayloadError,
    decode_task,
    encode_result,
    sign_payload,
    verify_payload,
)
from .task_executor import execute_task, TaskExecutionError


def _message(sender_id: str, message_type: str, payload: Dict[str, Any]) -> dict:
    return {
        "message_id": str(uuid.uuid4()),
        "sender_id": sender_id,
        "message_type": message_type,
        "payload": payload,
    }


def _error_response(task_id: str, error_type: str, error_message: str,
                    secret: str, receiver_id: str) -> dict:
    payload = {
        "task_id": task_id,
        "status": "FAILED",
        "error_type": error_type,
        "error_message": error_message,
    }
    payload["signature"] = sign_payload(payload, secret)
    return _message(receiver_id, "TASK_ERROR", payload)


def handle_task_message(
    message: dict,
    shared_secret: str,
    receiver_id: str = "meshweaver-worker",
) -> dict:
    """Authenticate, deserialize, execute and respond to a TASK_SUBMIT message.

    The sender must HMAC-sign the complete payload (excluding the signature
    field). The signature is checked BEFORE cloudpickle deserialization.
    """
    task_id = "unknown"
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

        # Do not call decode_task until the HMAC has been verified.
        function, args, kwargs = decode_task(payload.get("task_data"))
        result = execute_task(function, args, kwargs)
        response_payload = {
            "task_id": task_id,
            "status": "SUCCESS",
            "result_data": encode_result(result),
        }
        response_payload["signature"] = sign_payload(response_payload, shared_secret)
        return _message(receiver_id, "TASK_RESULT", response_payload)

    except (TaskPayloadError, TaskExecutionError, TypeError, ValueError,
            PermissionError) as error:
        return _error_response(
            task_id,
            type(error).__name__,
            str(error),
            shared_secret,
            receiver_id,
        )
    except Exception as error:
        return _error_response(
            task_id,
            type(error).__name__,
            "Unexpected task handler error.",
            shared_secret,
            receiver_id,
        )
