import unittest
from execution.task_codec import encode_task, sign_payload, decode_result
from execution.task_handler import handle_task_message

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
    def test_successful_task(self):
        response = handle_task_message(build_message(multiply, (6, 7), {}), SECRET)
        self.assertEqual(response["message_type"], "TASK_RESULT")
        self.assertEqual(response["payload"]["status"], "SUCCESS")
        self.assertEqual(decode_result(response["payload"]["result_data"]), 42)

    def test_task_execution_failure(self):
        response = handle_task_message(build_message(divide, (1, 0), {}), SECRET)
        self.assertEqual(response["message_type"], "TASK_ERROR")
        self.assertEqual(response["payload"]["error_type"], "TaskExecutionError")

    def test_modified_payload_rejected(self):
        message = build_message(multiply, (6, 7), {})
        message["payload"]["task_data"] = "tampered"
        response = handle_task_message(message, SECRET)
        self.assertEqual(response["message_type"], "TASK_ERROR")
        self.assertEqual(response["payload"]["error_type"], "PermissionError")

    def test_wrong_message_type_rejected(self):
        response = handle_task_message({"message_type": "PING", "payload": {}}, SECRET)
        self.assertEqual(response["message_type"], "TASK_ERROR")

    def test_response_signature_present(self):
        response = handle_task_message(build_message(multiply, (2, 3), {}), SECRET)
        self.assertIn("signature", response["payload"])


if __name__ == "__main__":
    unittest.main()
