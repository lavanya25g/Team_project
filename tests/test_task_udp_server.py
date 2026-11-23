import json
import unittest
from unittest.mock import patch

from execution.task_udp_server import UDPTaskServer
from execution.task_codec import (
    encode_task,
    sign_payload,
    decode_result
)
from execution.task_handler import handle_task_message


SECRET = "meshweaver-demo-secret-2026"


def add(a, b):
    return a + b


class FakeTransport:

    def __init__(self):
        self.sent = []

    def sendto(self, data, addr):
        self.sent.append((data, addr))


class TestUDPTaskServer(unittest.TestCase):

    def setUp(self):
        self.server = UDPTaskServer(SECRET)
        self.transport = FakeTransport()
        self.server.transport = self.transport
        self.addr = ("127.0.0.1", 50000)

    def test_valid_task_message_sends_result_to_sender(self):

        payload = {
            "task_id": "udp-test",
            "task_data": encode_task(add, (20, 22), {})
        }

        payload["signature"] = sign_payload(payload, SECRET)

        message = {
            "message_id": "message-1",
            "sender_id": "peer-a",
            "message_type": "TASK_SUBMIT",
            "payload": payload
        }

        self.server.datagram_received(
            json.dumps(message).encode("utf-8"),
            self.addr
        )

        self.assertEqual(len(self.transport.sent), 1)

        data, target = self.transport.sent[0]

        response = json.loads(data.decode("utf-8"))

        self.assertEqual(target, self.addr)
        self.assertEqual(response["message_type"], "TASK_RESULT")

        self.assertEqual(
            decode_result(response["payload"]["result_data"]),
            42
        )

    def test_duplicate_task_is_executed_only_once(self):

        payload = {
            "task_id": "duplicate-test",
            "task_data": encode_task(add, (10, 20), {})
        }

        payload["signature"] = sign_payload(payload, SECRET)

        message = {
            "message_id": "message-duplicate",
            "sender_id": "peer-a",
            "message_type": "TASK_SUBMIT",
            "payload": payload
        }

        data = json.dumps(message).encode("utf-8")

        with patch(
            "execution.task_udp_server.handle_task_message",
            wraps=handle_task_message
        ) as mocked_handler:

            self.server.datagram_received(data, self.addr)

            self.server.datagram_received(data, self.addr)

            self.assertEqual(mocked_handler.call_count, 1)

        self.assertEqual(len(self.transport.sent), 2)

        first_response = json.loads(
            self.transport.sent[0][0].decode("utf-8")
        )

        second_response = json.loads(
            self.transport.sent[1][0].decode("utf-8")
        )

        self.assertEqual(first_response, second_response)

        self.assertEqual(
            first_response["message_type"],
            "TASK_RESULT"
        )

    def test_malformed_json_is_ignored(self):

        self.server.datagram_received(
            b"not-json",
            self.addr
        )

        self.assertEqual(self.transport.sent, [])

    def test_invalid_secret_rejected(self):

        with self.assertRaises(ValueError):
            UDPTaskServer("short")


if __name__ == "__main__":
    unittest.main()