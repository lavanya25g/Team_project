# MeshWeaver – Week 2: Remote Task Transmission & Execution

This package implements the Himanshu-owned Week 2 execution components:

- `task_executor.py`: validates and executes a Python callable.
- `task_codec.py`: serializes function/arguments and results as Base64 strings; signs JSON payloads with HMAC-SHA256.
- `task_handler.py`: verifies incoming `TASK_SUBMIT`, runs it, and returns `TASK_RESULT` or `TASK_ERROR`.
- `remote_task.py`: submits tasks via Lavanya's `networking.client.send_message` API when available, with a temporary compatible asyncio UDP fallback before that package is merged.
- `peer_resolver.py`: resolves the current DHT IP-only records or future host/port records.
- `task_udp_server.py`: UDP worker that handles `TASK_SUBMIT` messages and replies to the sending address using Lavanya's JSON envelope.

## Install and run tests

From the repository root:

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

The serializer suite plus these Week 2 tests should run together. The Week 2 package adds 35 tests, including a real localhost UDP round-trip test.

## Shared secret

Both peers must use the same private shared secret of at least 16 characters. Store it in an environment variable; do not commit the secret:

```powershell
$env:MESHWEAVER_SHARED_SECRET = "replace-with-a-long-private-secret"
```

The example tests use a hard-coded test-only secret. Never reuse it in the actual network demo.

## Message payloads

`TASK_SUBMIT` payload:

```json
{
  "task_id": "uuid",
  "task_data": "BASE64_CLOUDPICKLE_BUNDLE",
  "signature": "HMAC_SHA256_HEX"
}
```

`TASK_RESULT` payload:

```json
{
  "task_id": "uuid",
  "status": "SUCCESS",
  "result_data": "BASE64_CLOUDPICKLE_RESULT",
  "signature": "HMAC_SHA256_HEX"
}
```

`TASK_ERROR` payload includes `task_id`, `status`, `error_type`, `error_message`, and `signature`.

The signature is verified before calling `cloudpickle.loads()` on the incoming task. This protects message integrity and authenticates possession of the shared secret. It does not replace a trusted-peer policy, secure key distribution, encryption, or network-level access controls.

## Connect to Lavanya's UDP client

After the `networking` package is present in the integrated working tree, the preferred integration is:

```python
import asyncio
import os
from networking.client import send_message
from execution.remote_task import submit_task


def add(a, b):
    return a + b

async def main():
    result = await submit_task(
        peer_host="127.0.0.1",
        peer_port=9999,
        sender_id="peer-a",
        function=add,
        args=(10, 20),
        shared_secret=os.environ["MESHWEAVER_SHARED_SECRET"],
        send_message_func=send_message,
    )
    print("Remote result:", result)

asyncio.run(main())
```

The current Lavanya `UDPServer` handles `PING`/`PONG` only. To demonstrate task execution before the team merges her server callback, run the separate `execution.task_udp_server.start_task_server()` worker on port `9998`; it follows the same JSON envelope and sends the response to the source address. Later, Lavanya can dispatch `TASK_SUBMIT` to `handle_task_message()` inside her existing UDP server so both message types share one server. Coordinate that change with her rather than independently overwriting her networking files.

The current Sanjana DHT `find_peer(peer_id)` returns an IP string without a port. Until DHT records include UDP ports, call `resolve_peer_endpoint(dht, peer_id, default_port=9999)` using the configured server port. Coordinate a shared `host:port` or `{host, port}` record format with Sanjana.

## Security warning

`cloudpickle.loads()` can execute arbitrary Python code. Do not accept tasks from unknown peers. HMAC authenticates payload integrity only when the shared secret remains private. Use trusted peers, private key distribution, network restrictions, task timeouts, and resource limits. Do not expose the demo worker to the public internet.

## Start the task worker

Start the worker in a separate terminal (replace the example secret with the same private value used by the sender):

```powershell
$env:MESHWEAVER_SHARED_SECRET = "replace-with-a-long-private-secret"
python -c "import asyncio, os; from execution.task_udp_server import start_task_server; asyncio.run(start_task_server(host='127.0.0.1', port=9998, shared_secret=os.environ['MESHWEAVER_SHARED_SECRET']))"
```

When `networking.client.send_message` is available locally, `submit_task()` uses it automatically. Until then, its temporary asyncio fallback uses the same JSON message envelope and can talk to this worker.

## Local UDP end-to-end test

The test suite starts a worker on an ephemeral localhost UDP port and submits a real task datagram to it. This validates the task request, worker dispatch, authenticated response, and result decoding without requiring teammates' branches to be merged. Run it with the full test command above.

## Run the local two-peer demonstration

Open Terminal 1 at the repository root:

```powershell
$env:MESHWEAVER_SHARED_SECRET = "use-a-private-secret-at-least-16-chars"
python -c "import asyncio, os; from execution.task_udp_server import start_task_server; asyncio.run(start_task_server(host='127.0.0.1', port=9998, shared_secret=os.environ['MESHWEAVER_SHARED_SECRET']))"
```

Open Terminal 2 at the same repository root and set the exact same secret:

```powershell
$env:MESHWEAVER_SHARED_SECRET = "use-a-private-secret-at-least-16-chars"
python demo_remote_task.py
```

Expected sender output: `Remote task result: 30`. This is a localhost integration demo; use a private network and trusted peers only.
