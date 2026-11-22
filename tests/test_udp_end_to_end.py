import asyncio
import os
import unittest

from execution.remote_task import submit_task
from execution.task_udp_server import UDPTaskServer

SECRET = "local-only-meshweaver-secret"


def multiply(a, b):
    return a * b


class TestUDPTaskEndToEnd(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        loop = asyncio.get_running_loop()
        self.transport, self.protocol = await loop.create_datagram_endpoint(
            lambda: UDPTaskServer(SECRET, receiver_id="peer-b"),
            local_addr=("127.0.0.1", 0),
        )
        self.host, self.port = self.transport.get_extra_info("sockname")[:2]

    async def asyncTearDown(self):
        self.transport.close()
        await asyncio.sleep(0)

    async def test_real_udp_remote_execution(self):
        result = await submit_task(
            peer_host=self.host,
            peer_port=self.port,
            sender_id="peer-a",
            function=multiply,
            args=(7, 6),
            shared_secret=SECRET,
        )
        self.assertEqual(result, 42)


if __name__ == "__main__":
    unittest.main()
