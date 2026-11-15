# MeshWeaver – Zero-Dependency P2P Async Task Broker

## Project Overview

MeshWeaver is a Peer-to-Peer (P2P) asynchronous task broker designed to allow multiple connected nodes to communicate, share resources, distribute tasks, and execute Python functions remotely.

The system aims to provide resource-aware task scheduling, peer discovery, fault detection, and distributed task execution without relying on a centralized task broker.

## Project Objectives

- Establish communication between multiple peer nodes.
- Enable peer registration and discovery using a Distributed Hash Table (DHT).
- Support Python function serialization and deserialization.
- Transmit tasks between remote peers.
- Execute tasks on available nodes and return results.
- Monitor CPU and RAM usage across peers.
- Implement resource-aware task scheduling.
- Detect peer failures using heartbeat mechanisms.
- Provide a live CLI dashboard for monitoring the system.

## Core Components

| Component | Description |
|---|---|
| P2P Networking | Asynchronous UDP communication between peers. |
| Distributed Hash Table (DHT) | Peer registration, discovery, and lookup. |
| Function Serialization | Convert Python functions into transferable bytes using cloudpickle. |
| Remote Task Execution | Transmit and execute tasks on remote peers. |
| Resource Monitoring | Monitor CPU and RAM usage. |
| Gossip Protocol | Share resource information between peers. |
| Task Scheduling | Assign tasks based on node availability and resource usage. |
| Fault Tolerance | Detect failed peers and report task failures. |
| CLI Dashboard | Display peer status, resource usage, and task information. |

## Technology Stack

- Python
- Asynchronous UDP Networking
- Distributed Hash Table (DHT)
- Cloudpickle
- Git and GitHub

Additional technologies and dependencies may be included as the project develops.

## Project Structure

```text
Team_project/
│
├── serialization/
│   ├── __init__.py
│   ├── serializer.py
│   └── README.md
│
├── tests/
│   └── test_serializer.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

The project structure will expand as the networking, DHT, scheduling, monitoring, and fault-tolerance components are integrated.

## Team Members

| Member | Primary Responsibility |
|---|---|
| Lavanya | Networking, integration, and task scheduling |
| Sanjana | DHT implementation and peer discovery |
| Himanshu Kumar | Function serialization, remote task execution, and result handling |
| Koteeswari | Resource monitoring, heartbeat, and CLI dashboard |

## Development Progress

### Week 1 – Foundation & Basic Implementation

- Asynchronous peer communication.
- Basic DHT data structures and peer registration.
- Python function serialization and deserialization.
- CPU/RAM monitoring and heartbeat mechanism.

### Week 2 – Peer Discovery & Communication

- Networking and DHT integration.
- Peer discovery and dynamic node joining.
- Remote task transmission and execution.
- Gossip-based resource sharing.

### Week 3 – Task Scheduling & Fault Tolerance

- Resource-aware task scheduling.
- Improved DHT routing.
- Task result handling and execution error management.
- Heartbeat-based failure detection.

### Week 4 – Security, Integration & Final Testing

- Module integration.
- Security implementation.
- Serialization and remote execution testing.
- Final dashboard and system testing.

**Note:** These are the planned project milestones. Individual implementation status should be updated as each component is completed and integrated.

## Installation

Clone the repository:

```bash
git clone https://github.com/lavanya25g/Team_project.git
```

Navigate to the project directory:

```bash
cd Team_project
```

Install the current dependencies:

```bash
python -m pip install -r requirements.txt
```

## Running Tests

Run the available unit tests from the project root:

```bash
python -m unittest discover -s tests -v
```

## Current Implementation

The serialization module currently provides:

- Python function serialization using cloudpickle.
- Function deserialization.
- Support for normal functions, lambda functions, and closures.
- Custom serialization and deserialization exceptions.
- Unit tests covering successful operations and invalid inputs.

The complete distributed task broker is under development.

## Security Considerations

Cloudpickle deserialization can execute arbitrary code. Therefore, serialized data should only be deserialized from trusted and authenticated peers.

Never deserialize untrusted data.

## Repository

GitHub: https://github.com/lavanya25g/Team_project
