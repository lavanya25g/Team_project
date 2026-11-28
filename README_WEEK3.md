# MeshWeaver – Week 3: Task Results & Execution Error Management

## Scope

This work extends the existing Week 2 remote-execution path. It does not add a
second networking implementation or a DHT peer resolver.

- Lavanya's networking layer remains responsible for UDP message transport.
- Sanjana's DHT remains responsible for peer discovery and lookup.
- This execution module handles task lifecycle, returned results, and
  execution/processing errors.
- Koteeswari's heartbeat and peer-failure detection remain separate.

## Task lifecycle

The worker records these states:

| State | Meaning |
|---|---|
| SUBMITTED | Authenticated task accepted by the worker |
| RUNNING | Task deserialization and execution started |
| SUCCESS | Result was serialized and recorded |
| FAILED | Deserialization, execution, or result processing failed |

The task results module provides a thread-safe, in-memory TaskResultTracker.
Each record includes the task ID, status, lifecycle timestamps, serialized
result data, or structured error details. The registry has a configurable
capacity, evicts the oldest completed records first, and never evicts active
tasks.

## Error handling

- The worker returns a signed TASK_ERROR for task-processing failures.
- When a user function raises an exception, the response exposes the original
  exception type and message (for example, ZeroDivisionError) instead of
  only reporting the wrapper exception.
- The submitting peer raises RemoteTaskError, which exposes task_id,
  error_type, and error_message attributes.
- Invalid or unauthenticated task payloads are rejected before
  cloudpickle.loads() is called.

## Run the tests

From the repository root:

~~~bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
~~~

## Inspect worker task status

A UDPTaskServer exposes its in-memory tracker as result_tracker. For example:

~~~python
from execution import UDPTaskServer

worker = UDPTaskServer(shared_secret="replace-with-a-private-secret")
# After the event loop receives tasks:
for task in worker.result_tracker.list_records():
    print(task["task_id"], task["status"])
~~~

This registry is process-local and is not a persistent database. Results are
retained only up to the configured capacity and are lost when the worker
process stops.

## Scope and security notes

This module does not perform peer-failure detection or task reassignment.
Those responsibilities remain with the heartbeat/fault-tolerance and
network-scheduling modules and must be coordinated with the relevant teammates.

cloudpickle.loads() can execute arbitrary code. Only process tasks from
trusted peers, verify signatures before deserialization, keep the shared
secret private, and do not expose the demo UDP worker to the public internet.
