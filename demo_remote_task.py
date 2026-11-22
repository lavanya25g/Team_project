"""Send a small demo task to a local MeshWeaver task worker."""

import asyncio
import os

from execution.remote_task import submit_task


def add(a, b):
    return a + b


async def main():
    secret = os.environ.get("MESHWEAVER_SHARED_SECRET")
    if not secret:
        raise RuntimeError("Set MESHWEAVER_SHARED_SECRET in this terminal first.")

    result = await submit_task(
        peer_host="127.0.0.1",
        peer_port=9998,
        sender_id="peer-a",
        function=add,
        args=(10, 20),
        shared_secret=secret,
    )
    print("Remote task result:", result)


if __name__ == "__main__":
    asyncio.run(main())
