
# MeshWeaver – P2P Async Task Broker

MeshWeaver is a Peer-to-Peer (P2P) task broker designed to allow multiple computers (nodes) to communicate and distribute tasks across available resources.

## Features Implemented in Lavanya Branch

### 1. UDP Networking
- Asynchronous UDP server and client using Python `asyncio`.
- JSON-based message encoding and decoding.
- Unique message IDs for message identification.
- PING/PONG communication between peers.
- Configurable server host and port.
- UDP-based asynchronous message transmission and reception.

### 2. CPU and RAM Resource Monitoring
- CPU usage monitoring using `psutil`.
- RAM usage monitoring.
- Reports total, used, and available RAM in MB.
- Identifies the reporting node using its node ID.
- Includes UTC timestamps in resource reports.
- Configurable monitoring interval (default: 5 seconds).

### 3. Resource Monitoring and UDP Integration
- Collects CPU and RAM usage from the local node.
- Sends resource reports to peers using `RESOURCE_UPDATE` messages.
- Receives and displays resource reports through the UDP server.
- Sends `RESOURCE_ACK` responses to confirm receipt of resource reports.
- Supports resource information exchange through the existing JSON-based message protocol.
- Successfully tested resource-report transmission and acknowledgement using local UDP communication.

### 4. Testing
- Unit tests for resource monitoring.
- Validation of resource report fields and values.
- Tests for node identification.
- Networking protocol tests.
- Manual testing of UDP resource-report transmission and acknowledgement.


### CPU and RAM Resource Monitoring

MeshWeaver includes a resource monitoring module that collects system resource usage using Python's `psutil` library.

**Monitored information:**
- CPU usage percentage
- Total RAM
- Used RAM
- Available RAM
- Node ID
- UTC timestamp

**UDP Integration:**
- Resource reports are sent between nodes using `RESOURCE_UPDATE` messages.
- The receiving UDP server displays the received resource information.
- The server responds with a `RESOURCE_ACK` message to confirm receipt.

**Run resource monitoring:**
```bash
py -m monitoring.resource_monitor
```

**Test resource monitoring:**
```bash
py -m unittest test_resource_monitor -v
```

**Test UDP resource reporting:**

Start the server:
```bash
py -m networking.server
```

Run the client in another terminal:
```bash
py -m networking.client
```

**Status:** Implemented and locally tested.


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
├── requirements.txt
├── test_protocol.py
├── test_resource_monitor.py
└── README.md
```

## Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/lavanya25g/Team_project.git
cd Team_project
pip install -r requirements.txt
```

## Running the UDP Server

```bash
py -m networking.server
```

## Running the UDP Client

Open another terminal and run:

```bash
py -m networking.client
```

The client collects local CPU and RAM usage, sends a `RESOURCE_UPDATE` message to the UDP server, and receives a `RESOURCE_ACK` response.

## Running Resource Monitoring Independently

```bash
py -m monitoring.resource_monitor
```

The monitor displays CPU and RAM usage for the local node at approximately five-second intervals.

Press `Ctrl + C` to stop monitoring.

## Running Tests

Run the resource monitoring tests:

```bash
py -m unittest test_resource_monitor -v
```

Run the networking protocol tests:

```bash
py -m unittest test_protocol -v
```

Run all discovered unit tests:

```bash
py -m unittest discover -v
```

## Technologies Used

- Python
- Asyncio
- UDP
- JSON
- psutil
- unittest
- Git and GitHub

## Development Status

The following components have been implemented in the `Lavanya` branch:

- Asynchronous UDP networking.
- JSON-based message protocol.
- PING/PONG communication.
- CPU and RAM resource monitoring.
- Resource-report transmission using `RESOURCE_UPDATE`.
- Resource-report reception through the UDP server.
- Acknowledgement handling using `RESOURCE_ACK`.
- Local resource-report transmission and acknowledgement testing.

### Upcoming Work
- Integration with DHT-based peer discovery.
- Resource-aware peer selection and task scheduling.
- Integration with remote task execution.
- Multi-machine communication and end-to-end testing.

---

**Repository:** https://github.com/lavanya25g/Team_project
