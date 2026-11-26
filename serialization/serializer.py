import cloudpickle
import pickle
from typing import Any, Callable

"""Function serialization utilities for the MeshWeaver project."""


class SerializationError(Exception):
    """Raised when function serialization fails."""


class DeserializationError(Exception):
    """Raised when function deserialization fails."""


def serialize_function(func: Callable[..., Any]) -> bytes:
    """
    Serialize a Python function into bytes using cloudpickle.
    """

    if not callable(func):
        raise TypeError("Input must be a callable function.")

    try:
        serialized_data = cloudpickle.dumps(
            func,
            protocol=pickle.HIGHEST_PROTOCOL
        )
        return serialized_data

    except Exception as error:
        raise SerializationError(
            "Failed to serialize function."
        ) from error


def deserialize_function(data: bytes) -> Callable[..., Any]:
    """
    Deserialize bytes back into a Python callable.
    """

    if not isinstance(data, bytes):
        raise TypeError("Input must be bytes.")

    try:
        function = cloudpickle.loads(data)

        if not callable(function):
            raise DeserializationError(
                "Deserialized object is not callable."
            )

        return function

    except DeserializationError:
        raise

    except Exception as error:
        raise DeserializationError(
            "Failed to deserialize function."
        ) from error