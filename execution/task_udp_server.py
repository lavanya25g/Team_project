"""UDP worker with authenticated task handling and duplicate protection."""

import asyncio
import json
from collections import OrderedDict
from typing import Optional

from .task_handler import handle_task_message
from .task_codec import verify_payload
from .task_results import TaskResultTracker


class UDPTaskServer(asyncio.DatagramProtocol):
    """Receive task datagrams and retain a bounded task-result history."""

    def __init__(
        self,
        shared_secret: str,
        receiver_id: str = "meshweaver-worker",
        max_cached_responses: int = 1000,
        result_tracker: Optional[TaskResultTracker] = None,
    ):
        if not isinstance(shared_secret, str) or len(shared_secret) < 16:
            raise ValueError("shared_secret must contain at least 16 characters.")
        if (
            isinstance(max_cached_responses, bool)
            or not isinstance(max_cached_responses, int)
            or max_cached_responses <= 0
        ):
            raise ValueError("Cache size must be a positive integer.")

        self.shared_secret = shared_secret
        self.receiver_id = receiver_id
        self.max_cached_responses = max_cached_responses
        self.response_cache = OrderedDict()
        self.result_tracker = (
            result_tracker
            if result_tracker is not None
            else TaskResultTracker(max_records=max_cached_responses)
        )
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        address = transport.get_extra_info("sockname")
        print(f"MeshWeaver task worker listening at {address}")

    def datagram_received(self, data: bytes, addr):
        try:
            message = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            print(f"Rejected malformed UDP message from {addr}: {error}")
            return

        cache_key = None
        payload = message.get("payload") if isinstance(message, dict) else None

        # Authenticate before using the cache or processing serialized data.
        if (
            isinstance(message, dict)
            and message.get("message_type") == "TASK_SUBMIT"
            and isinstance(payload, dict)
        ):
            task_id = payload.get("task_id")
            signature = payload.get("signature")
            if (
                isinstance(task_id, str)
                and task_id
                and verify_payload(payload, self.shared_secret)
            ):
                cache_key = (task_id, signature)
                cached_response = self.response_cache.get(cache_key)
                if cached_response is not None:
                    self.response_cache.move_to_end(cache_key)
                    self.transport.sendto(
                        json.dumps(cached_response).encode("utf-8"),
                        addr,
                    )
                    return

        try:
            response = handle_task_message(
                message,
                shared_secret=self.shared_secret,
                receiver_id=self.receiver_id,
                result_tracker=self.result_tracker,
            )
            self.transport.sendto(json.dumps(response).encode("utf-8"), addr)

            if cache_key is not None:
                self.response_cache[cache_key] = response
                self.response_cache.move_to_end(cache_key)
                while len(self.response_cache) > self.max_cached_responses:
                    self.response_cache.popitem(last=False)
        except Exception as error:
            print(f"UDP task worker error from {addr}: {error}")

    def error_received(self, error):
        print(f"UDP task worker socket error: {error}")


async def start_task_server(
    host: str = "127.0.0.1",
    port: int = 9998,
    shared_secret: Optional[str] = None,
    receiver_id: str = "meshweaver-worker",
):
    if shared_secret is None:
        raise ValueError("A shared_secret is required.")

    loop = asyncio.get_running_loop()
    transport, _protocol = await loop.create_datagram_endpoint(
        lambda: UDPTaskServer(shared_secret, receiver_id),
        local_addr=(host, port),
    )
    try:
        await asyncio.Future()
    finally:
        transport.close()
