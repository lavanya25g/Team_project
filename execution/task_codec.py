"""Encode tasks/results for JSON transport and authenticate payloads.

WARNING: cloudpickle.loads can execute arbitrary code. Always verify the
HMAC signature and trust the sending peer before calling decode_task().
"""

import base64
import binascii
import cloudpickle
import hashlib
import hmac
import json
import pickle
from typing import Any, Dict, Tuple


class TaskPayloadError(ValueError):
    """Raised when a task or result payload is invalid."""


def _validate_secret(secret: str) -> None:
    if not isinstance(secret, str) or len(secret) < 16:
        raise ValueError("Shared secret must be a string of at least 16 characters.")


def encode_task(function: Any, args: tuple = (), kwargs: dict = None) -> str:
    """Serialize a function and its arguments into a Base64 ASCII string."""
    if not callable(function):
        raise TypeError("Task must be a callable function.")
    if not isinstance(args, tuple):
        raise TypeError("Task positional arguments must be a tuple.")
    if kwargs is None:
        kwargs = {}
    if not isinstance(kwargs, dict):
        raise TypeError("Task keyword arguments must be a dictionary.")

    bundle = {"function": function, "args": args, "kwargs": kwargs}
    try:
        raw = cloudpickle.dumps(bundle, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as error:
        raise TaskPayloadError("Could not serialize task.") from error
    return base64.b64encode(raw).decode("ascii")


def decode_task(task_data: str) -> Tuple[Any, tuple, dict]:
    """Decode task data. Call only after verifying its message signature."""
    if not isinstance(task_data, str):
        raise TaskPayloadError("Task data must be a Base64 string.")
    try:
        raw = base64.b64decode(task_data.encode("ascii"), validate=True)
        bundle = cloudpickle.loads(raw)
    except (UnicodeEncodeError, binascii.Error, ValueError, TypeError) as error:
        raise TaskPayloadError("Task data is not valid Base64/cloudpickle data.") from error
    except Exception as error:
        raise TaskPayloadError("Task data could not be deserialized.") from error

    if not isinstance(bundle, dict):
        raise TaskPayloadError("Decoded task must be a dictionary.")
    function = bundle.get("function")
    args = bundle.get("args")
    kwargs = bundle.get("kwargs")
    if not callable(function):
        raise TaskPayloadError("Decoded task function is not callable.")
    if not isinstance(args, tuple):
        raise TaskPayloadError("Decoded task arguments must be a tuple.")
    if not isinstance(kwargs, dict):
        raise TaskPayloadError("Decoded task keyword arguments must be a dictionary.")
    return function, args, kwargs


def encode_result(result: Any) -> str:
    """Serialize a task result into a Base64 ASCII string."""
    try:
        raw = cloudpickle.dumps(result, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as error:
        raise TaskPayloadError("Could not serialize task result.") from error
    return base64.b64encode(raw).decode("ascii")


def decode_result(result_data: str) -> Any:
    """Decode result data. Verify the response signature before calling this."""
    if not isinstance(result_data, str):
        raise TaskPayloadError("Result data must be a Base64 string.")
    try:
        raw = base64.b64decode(result_data.encode("ascii"), validate=True)
        return cloudpickle.loads(raw)
    except Exception as error:
        raise TaskPayloadError("Result data could not be decoded.") from error


def _canonical_payload(payload: Dict[str, Any]) -> bytes:
    if not isinstance(payload, dict):
        raise TypeError("Message payload must be a dictionary.")
    unsigned = {key: value for key, value in payload.items() if key != "signature"}
    try:
        return json.dumps(
            unsigned,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise ValueError("Payload must contain JSON-serializable values.") from error


def sign_payload(payload: Dict[str, Any], secret: str) -> str:
    """Return an HMAC-SHA256 signature for a JSON-compatible payload."""
    _validate_secret(secret)
    digest = hmac.new(
        secret.encode("utf-8"), _canonical_payload(payload), hashlib.sha256
    )
    return digest.hexdigest()


def verify_payload(payload: Dict[str, Any], secret: str) -> bool:
    """Verify the signature in a payload without deserializing its contents."""
    try:
        supplied = payload.get("signature")
        if not isinstance(supplied, str):
            return False
        expected = sign_payload(payload, secret)
        return hmac.compare_digest(supplied, expected)
    except (TypeError, ValueError):
        return False
