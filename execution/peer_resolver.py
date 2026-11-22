"""Resolve a DHT peer record to a (host, UDP port) endpoint."""


class PeerResolutionError(ValueError):
    """Raised when a DHT record cannot be converted to a UDP endpoint."""


def resolve_peer_endpoint(dht, peer_id: str, default_port: int = None):
    """Resolve a peer using DHT.find_peer(peer_id).

    Supported DHT records:
      - {"host": "127.0.0.1", "port": 9999}
      - ("127.0.0.1", 9999)
      - "127.0.0.1:9999"
      - "127.0.0.1" when default_port is supplied (current DHT format)

    The current Sanjana DHT stores an IP string only, so pass the configured
    UDP server port as default_port until the DHT record is extended.
    """
    if not isinstance(peer_id, str) or not peer_id:
        raise PeerResolutionError("Peer ID must be a non-empty string.")
    try:
        record = dht.find_peer(peer_id)
    except AttributeError as error:
        raise PeerResolutionError("DHT object must provide find_peer().") from error
    if record is None:
        raise PeerResolutionError(f"Peer {peer_id!r} was not found in the DHT.")

    if isinstance(record, dict):
        host, port = record.get("host"), record.get("port")
    elif isinstance(record, (tuple, list)) and len(record) == 2:
        host, port = record
    elif isinstance(record, str):
        if record.count(":") == 1:
            host, port_text = record.rsplit(":", 1)
            try:
                port = int(port_text)
            except ValueError as error:
                raise PeerResolutionError("DHT peer port is not an integer.") from error
        else:
            host, port = record, default_port
    else:
        raise PeerResolutionError("Unsupported DHT peer record format.")

    if not isinstance(host, str) or not host.strip():
        raise PeerResolutionError("DHT peer host is missing.")
    if not isinstance(port, int) or not 1 <= port <= 65535:
        raise PeerResolutionError(
            "UDP port is missing or invalid; provide default_port or store host:port in DHT."
        )
    return host, port
