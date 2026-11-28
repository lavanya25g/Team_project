"""Client-side helper for submitting a task to a remote MeshWeaver peer."""

import asyncio
import json
import uuid
from typing import Any, Callable, Optional

from .task_codec import encode_task, decode_result, sign_payload, verify_payload


class _OneShotUDPClient(asyncio.DatagramProtocol):
    """Small fallback transport using the same JSON envelope as Lavanya's client."""

    def __init__(self, message: dict, response_future: asyncio.Future):
        self.message = message
        self.response_future = response_future
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        self.transport.sendto(json.dumps(self.message).encode("utf-8"))

    def datagram_received(self, data: bytes, addr):
        try:
            response = json.loads(data.decode("utf-8"))
            if not self.response_future.done():
                self.response_future.set_result(response)
        except Exception as error:
            if not self.response_future.done():
                self.response_future.set_exception(error)

    def error_received(self, error):
        if not self.response_future.done():
            self.response_future.set_exception(error)


async def _fallback_send_message(
    peer_host: str, peer_port: int, sender_id: str, message_type: str, payload=None
):
    """Temporary transport fallback until networking.client is merged locally."""
    loop = asyncio.get_running_loop()
    message = {
        "message_id": str(uuid.uuid4()),
        "sender_id": sender_id,
        "message_type": message_type,
        "payload": payload or {},
    }
    response_future = loop.create_future()
    transport, _protocol = await loop.create_datagram_endpoint(
        lambda: _OneShotUDPClient(message, response_future),
        remote_addr=(peer_host, peer_port),
    )
    try:
        return await asyncio.wait_for(response_future, timeout=5)
    finally:
        transport.close()


class RemoteTaskError(RuntimeError):
    """Raised when the remote peer reports a task execution failure."""

    def __init__(self, task_id: str, error_type: str, error_message: str):
        self.task_id = task_id
        self.error_type = error_type
        self.error_message = error_message
        super().__init__(f"{error_type}: {error_message}")


class RemoteTaskProtocolError(RuntimeError):
    """Raised when the remote peer returns an invalid response."""


async def submit_task(
    peer_host: str,
    peer_port: int,
    sender_id: str,
    function: Callable[..., Any],
    args: tuple = (),
    kwargs: Optional[dict] = None,
    shared_secret: Optional[str] = None,
    send_message_func: Optional[Callable[..., Any]] = None,
) -> Any:
    """Submit a task over the existing networking client's send_message API.

    The send_message_func argument is injectable for tests. In the integrated
    app pass networking.client.send_message. This keeps execution tests
    independent of the networking branch until that package is merged.
    """
    if not isinstance(peer_host, str) or not peer_host:
        raise ValueError("Peer host must be a non-empty string.")
    if (
        not isinstance(peer_port, int)
        or isinstance(peer_port, bool)
        or not 1 <= peer_port <= 65535
    ):
        raise ValueError("Peer port must be between 1 and 65535.")
    if not isinstance(sender_id, str) or not sender_id:
        raise ValueError("Sender ID must be a non-empty string.")
    if not isinstance(shared_secret, str) or len(shared_secret) < 16:
        raise ValueError("Shared secret must contain at least 16 characters.")
    if kwargs is None:
        kwargs = {}
    if not isinstance(kwargs, dict):
        raise TypeError("kwargs must be a dictionary.")

    if send_message_func is None:
        try:
            from networking.client import send_message
        except ImportError:
            # Temporary fallback keeps the task demo testable before the
            # networking package is merged. It uses the same JSON envelope.
            send_message_func = _fallback_send_message
        else:
            send_message_func = send_message

    task_id = str(uuid.uuid4())
    payload = {
        "task_id": task_id,
        "task_data": encode_task(function, args, kwargs),
    }
    payload["signature"] = sign_payload(payload, shared_secret)

    response = await send_message_func(
        peer_host=peer_host,
        peer_port=peer_port,
        sender_id=sender_id,
        message_type="TASK_SUBMIT",
        payload=payload,
    )
    if response is None:
        raise TimeoutError("Remote peer did not respond to the task request.")
    if not isinstance(response, dict):
        raise RemoteTaskProtocolError("Remote response must be a dictionary.")

    message_type = response.get("message_type")
    response_payload = response.get("payload")
    if message_type not in {"TASK_RESULT", "TASK_ERROR"}:
        raise RemoteTaskProtocolError(
            f"Unexpected response message type: {message_type!r}"
        )
    if not isinstance(response_payload, dict):
        raise RemoteTaskProtocolError("Remote response payload is invalid.")
    if response_payload.get("task_id") != task_id:
        raise RemoteTaskProtocolError("Response task ID does not match request.")
    if not verify_payload(response_payload, shared_secret):
        raise RemoteTaskProtocolError("Remote response authentication failed.")

    if message_type == "TASK_ERROR":
        error_type = response_payload.get("error_type", "RemoteTaskError")
        error_message = response_payload.get("error_message", "Remote execution failed.")
        if not isinstance(error_type, str) or not isinstance(error_message, str):
            raise RemoteTaskProtocolError("Remote error details are invalid.")
        raise RemoteTaskError(task_id, error_type, error_message)

    if response_payload.get("status") != "SUCCESS":
        raise RemoteTaskProtocolError("TASK_RESULT did not contain SUCCESS status.")
    try:
        return decode_result(response_payload.get("result_data"))
    except Exception as error:
        raise RemoteTaskProtocolError("Could not decode remote task result.") from error
