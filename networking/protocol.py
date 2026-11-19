
import json
import uuid


def create_message(sender_id, message_type, payload=None):
    """
    Create a standard message for communication
    between MeshWeaver nodes.
    """

    message = {
        "message_id": str(uuid.uuid4()),
        "sender_id": sender_id,
        "message_type": message_type,
        "payload": payload or {}
    }

    return message


def encode_message(message):
    """Convert a Python dictionary into JSON bytes."""

    return json.dumps(message).encode("utf-8")


def decode_message(data):
    """Convert received JSON bytes into a Python dictionary."""

    return json.loads(data.decode("utf-8"))
