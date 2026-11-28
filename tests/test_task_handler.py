import unittest

from execution.task_codec import encode_task, sign_payload, decode_result
from execution.task_handler import handle_task_message
from execution.task_results import TaskResultTracker


SECRET = "meshweaver-demo-secret-2026"


def multiply(a, b):
    return a * b


def divide(a, b):
    return a / b


def build_message(function, args, kwargs, task_id="task-1"):
    payload = {"task_id": task_id, "task_data": encode_task(function, args, kwargs)}
    payload["signature"] = sign_payload(payload, SECRET)
    return {
        "message_id": "message-1",
        "sender_id": "peer-a",
        "message_type": "TASK_SUBMIT",
        "payload": payload,
    }


class TestTaskHandler(unittest.TestCase):
    def setUp(self):
        self.tracker = TaskResultTracker()

    def test_successful_task_and_result_tracking(self):
        response = handle_task_message(
            build_message(multiply, (6, 7), {}),
            SECRET,
            result_tracker=self.tracker,
        )
        self.assertEqual(response["message_type"], "TASK_RESULT")
        self.assertEqual(response["payload"]["status"], "SUCCESS")
        self.assertEqual(decode_result(response["payload"]["result_data"]), 42)
        record = self.tracker.get("task-1")
        self.assertEqual(record["status"], "SUCCESS")
        self.assertEqual(record["result_data"], response["payload"]["result_data"])

    def test_task_execution_failure_preserves_original_error(self):
        response = handle_task_message(
            build_message(divide, (1, 0), {}),
            SECRET,
            result_tracker=self.tracker,
        )
        self.assertEqual(response["message_type"], "TASK_ERROR")
        self.assertEqual(response["payload"]["status"], "FAILED")
        self.assertEqual(response["payload"]["error_type"], "ZeroDivisionError")
        self.assertEqual(self.tracker.get("task-1")["status"], "FAILED")

    def test_modified_payload_rejected_before_deserialization(self):
        message = build_message(multiply, (6, 7), {})
        message["payload"]["task_data"] = "tampered"
        response = handle_task_message(message, SECRET, result_tracker=self.tracker)
        self.assertEqual(response["message_type"], "TASK_ERROR")
        self.assertEqual(response["payload"]["error_type"], "PermissionError")
        self.assertEqual(self.tracker.list_records(), [])

    def test_wrong_message_type_rejected(self):
        response = handle_task_message({"message_type": "PING", "payload": {}}, SECRET)
        self.assertEqual(response["message_type"], "TASK_ERROR")

    def test_response_signature_present(self):
        response = handle_task_message(build_message(multiply, (2, 3), {}), SECRET)
        self.assertIn("signature", response["payload"])

    def test_invalid_task_payload_is_tracked_as_failed(self):
        payload = {"task_id": "bad-task", "task_data": "not-base64"}
        payload["signature"] = sign_payload(payload, SECRET)
        message = {
            "message_id": "bad-message",
            "sender_id": "peer-a",
            "message_type": "TASK_SUBMIT",
            "payload": payload,
        }
        response = handle_task_message(message, SECRET, result_tracker=self.tracker)
        self.assertEqual(response["message_type"], "TASK_ERROR")
        self.assertEqual(self.tracker.get("bad-task")["status"], "FAILED")


if __name__ == "__main__":
    unittest.main()
