"""Small UDP worker endpoint for TASK_SUBMIT messages.

It follows Lavanya's JSON message envelope and can be replaced by a callback
inside networking.server. It does not modify or duplicate the DHT component.
"""

import asyncio
import json
from typing import Optional

from .task_handler import handle_task_message


class UDPTaskServer(asyncio.DatagramProtocol):
    def __init__(self, shared_secret: str, receiver_id: str = "meshweaver-worker"):
        if not isinstance(shared_secret, str) or len(shared_secret) < 16:
            raise ValueError("Shared secret must contain at least 16 characters.")
        self.shared_secret = shared_secret
        self.receiver_id = receiver_id
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        print(f"MeshWeaver task worker listening at {transport.get_extra_info('sockname')}")

    def datagram_received(self, data: bytes, addr):
        try:
            message = json.loads(data.decode("utf-8"))
            response = handle_task_message(
                message,
                shared_secret=self.shared_secret,
                receiver_id=self.receiver_id,
            )
            self.transport.sendto(
                json.dumps(response).encode("utf-8"),
                addr,
            )
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as error:
            print(f"Rejected malformed UDP task message from {addr}: {error}")
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
    """Start the task worker. Use a private network and trusted peers only."""
    if shared_secret is None:
        raise ValueError("A shared_secret is required to start the task worker.")
    loop = asyncio.get_running_loop()
    transport, _protocol = await loop.create_datagram_endpoint(
        lambda: UDPTaskServer(shared_secret, receiver_id),
        local_addr=(host, port),
    )
    try:
        await asyncio.Future()
    finally:
        transport.close()
