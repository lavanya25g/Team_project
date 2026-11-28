import json
import unittest
from unittest.mock import patch

from execution.task_codec import encode_task, sign_payload, decode_result
from execution.task_handler import handle_task_message
from execution.task_udp_server import UDPTaskServer

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

    def build_message(self, task_id):
        payload = {
            "task_id": task_id,
            "task_data": encode_task(add, (20, 22), {}),
        }
        payload["signature"] = sign_payload(payload, SECRET)
        return {
            "message_id": "message-1",
            "sender_id": "peer-a",
            "message_type": "TASK_SUBMIT",
            "payload": payload,
        }

    def test_successful_task_is_recorded(self):
        self.server.datagram_received(
            json.dumps(self.build_message("udp-test")).encode("utf-8"),
            self.addr,
        )
        self.assertEqual(len(self.transport.sent), 1)
        data, target = self.transport.sent[0]
        response = json.loads(data.decode("utf-8"))
        self.assertEqual(target, self.addr)
        self.assertEqual(response["message_type"], "TASK_RESULT")
        self.assertEqual(decode_result(response["payload"]["result_data"]), 42)
        self.assertEqual(self.server.result_tracker.get("udp-test")["status"], "SUCCESS")

    def test_duplicate_task_is_executed_once_and_tracked_once(self):
        message = self.build_message("duplicate-test")
        data = json.dumps(message).encode("utf-8")
        with patch(
            "execution.task_udp_server.handle_task_message",
            wraps=handle_task_message,
        ) as mocked_handler:
            self.server.datagram_received(data, self.addr)
            self.server.datagram_received(data, self.addr)
            self.assertEqual(mocked_handler.call_count, 1)

        self.assertEqual(len(self.transport.sent), 2)
        self.assertEqual(len(self.server.result_tracker.list_records()), 1)
        self.assertEqual(
            self.server.result_tracker.get("duplicate-test")["status"],
            "SUCCESS",
        )

    def test_malformed_json_is_ignored(self):
        self.server.datagram_received(b"not-json", self.addr)
        self.assertEqual(self.transport.sent, [])

    def test_invalid_secret_rejected(self):
        with self.assertRaises(ValueError):
            UDPTaskServer("short")


if __name__ == "__main__":
    unittest.main()
