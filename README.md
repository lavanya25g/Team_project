# MeshWeaver – P2P Async Task Broker

## Project Overview

MeshWeaver is a Peer-to-Peer (P2P) asynchronous task broker designed to connect multiple nodes, share system resources, distribute computational tasks, and support remote Python function execution.

The project aims to provide decentralized task scheduling, peer discovery, resource monitoring, fault detection, and distributed execution without depending on a centralized task broker.

## Key Features

The planned system includes:

- **Peer-to-Peer Communication:** Asynchronous communication between connected nodes using UDP.
- **Message Protocol:** Structured JSON messages with unique message IDs, sender IDs, message types, and payloads.
- **Peer Discovery:** Discovering and maintaining information about available peers using a Distributed Hash Table (DHT).
- **Resource Monitoring:** Monitoring CPU and RAM utilization across participating nodes.
- **Resource-Aware Scheduling:** Selecting suitable peers based on their available system resources.
- **Remote Task Execution:** Supporting serialization and execution of Python functions on remote nodes.
- **Fault Detection:** Detecting unavailable peers through heartbeat and gossip mechanisms.

## Technology Stack

- **Language:** Python
- **Networking:** Asyncio, UDP
- **Message Format:** JSON
- **Peer Discovery:** Distributed Hash Table (DHT)
- **Serialization:** Cloudpickle (planned integration)
- **Resource Monitoring:** psutil
- **Version Control:** Git and GitHub

## Project Structure

```text
MeshWeaver/
│
├── networking/
│   ├── __init__.py
│   ├── node.py
│   ├── protocol.py
│   ├── server.py
│   └── client.py
│
├── monitoring/
│   ├── __init__.py
│   └── resource_monitor.py
│
├── test_protocol.py
├── test_resource_monitor.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Current Implementation Status

| Component | Status |
|---|---|
| JSON Message Protocol | Implemented |
| Asynchronous UDP Server | Implemented |
| Asynchronous UDP Client | Implemented |
| PING–PONG Communication | Tested |
| Peer Discovery and DHT | In Development |
| Function Serialization | In Development |
| Remote Function Execution | In Development |
| CPU/RAM Monitoring | Implemented (standalone) |
| Heartbeat and Gossip | In Development |
| Resource-Aware Task Scheduling | In Development |
| Main System Integration | Pending |

## Getting Started

### Prerequisites

- Python 3.10 or later
- Git

### Clone the Repository

```bash
git clone https://github.com/lavanya25g/Team_project.git
cd Team_project
```

### Install Dependencies

```bash
py -m pip install -r requirements.txt
```

### Start the UDP Server

Open a terminal and run:

```bash
py -m networking.server
```

The server starts on the default address `127.0.0.1:9999`.

### Start the UDP Client

Open another terminal and run:

```bash
py -m networking.client
```

The client sends a PING message and waits for a PONG response from the server.

### Run Resource Monitoring

```bash
py -m monitoring.resource_monitor
```

The resource monitor displays local CPU and RAM usage at approximately five-second intervals.

Press `Ctrl + C` to stop monitoring.

**Note:** The current default networking configuration is intended for local testing. Communication between different machines will require appropriate network host and port configuration.

## Message Protocol

MeshWeaver uses a structured JSON message format.

Example:

```json
{
    "message_id": "unique-uuid",
    "sender_id": "peer_1",
    "message_type": "PING",
    "payload": {
        "status": "checking"
    }
}
```

The networking protocol currently supports:

- `PING`
- `PONG`

Additional message types will be introduced as peer discovery and distributed execution are integrated.

## Team Contributions

| Team Member | Responsibility |
|---|---|
| Lavanya | Networking, asynchronous communication, CPU/RAM resource monitoring, resource-aware task scheduling and integration |
| Sanjana | DHT implementation and peer discovery |
| Himanshu | Serialization and remote function execution |

## Project Goal

The ultimate goal of MeshWeaver is to build a decentralized, resource-aware task execution system in which multiple nodes can discover each other, communicate asynchronously, and distribute computational workloads efficiently.

---

**Project:** MeshWeaver

**Repository:** https://github.com/lavanya25g/Team_project
