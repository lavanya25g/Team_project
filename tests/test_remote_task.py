import unittest

from execution.remote_task import submit_task, RemoteTaskError
from execution.task_handler import handle_task_message

SECRET = "meshweaver-demo-secret-2026"


def add(a, b):
    return a + b


def fail():
    raise RuntimeError("demo failure")


class TestRemoteTask(unittest.IsolatedAsyncioTestCase):
    async def fake_send_message(self, **message_args):
        incoming = {
            "message_id": "msg-test",
            "sender_id": message_args["sender_id"],
            "message_type": message_args["message_type"],
            "payload": message_args["payload"],
        }
        return handle_task_message(incoming, SECRET, receiver_id="peer-b")

    async def test_submit_task_round_trip(self):
        result = await submit_task(
            "127.0.0.1", 9999, "peer-a", add,
            args=(12, 30), shared_secret=SECRET,
            send_message_func=self.fake_send_message,
        )
        self.assertEqual(result, 42)

    async def test_remote_execution_error_contains_details(self):
        with self.assertRaises(RemoteTaskError) as raised:
            await submit_task(
                "127.0.0.1", 9999, "peer-a", fail,
                shared_secret=SECRET,
                send_message_func=self.fake_send_message,
            )
        self.assertEqual(raised.exception.error_type, "RuntimeError")
        self.assertEqual(raised.exception.error_message, "demo failure")
        self.assertTrue(raised.exception.task_id)

    async def test_invalid_port(self):
        with self.assertRaises(ValueError):
            await submit_task(
                "127.0.0.1", 70000, "peer-a", add,
                args=(1, 2), shared_secret=SECRET,
                send_message_func=self.fake_send_message,
            )

    async def test_boolean_port_rejected(self):
        with self.assertRaises(ValueError):
            await submit_task(
                "127.0.0.1", True, "peer-a", add,
                args=(1, 2), shared_secret=SECRET,
                send_message_func=self.fake_send_message,
            )


if __name__ == "__main__":
    unittest.main()
