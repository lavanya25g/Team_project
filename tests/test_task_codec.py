import unittest
from execution.task_codec import (
    TaskPayloadError, encode_task, decode_task, encode_result, decode_result,
    sign_payload, verify_payload,
)

SECRET = "meshweaver-demo-secret-2026"


def add(a, b):
    return a + b


class TestTaskCodec(unittest.TestCase):
    def test_encode_decode_function_and_args(self):
        task_data = encode_task(add, (2, 3), {})
        function, args, kwargs = decode_task(task_data)
        self.assertTrue(callable(function))
        self.assertEqual(function(*args, **kwargs), 5)

    def test_encode_decode_keyword_args(self):
        task_data = encode_task(add, (), {"a": 4, "b": 6})
        function, args, kwargs = decode_task(task_data)
        self.assertEqual(function(*args, **kwargs), 10)

    def test_reject_non_callable(self):
        with self.assertRaises(TypeError):
            encode_task(123)

    def test_reject_wrong_args_type(self):
        with self.assertRaises(TypeError):
            encode_task(add, [1, 2], {})

    def test_result_round_trip(self):
        self.assertEqual(decode_result(encode_result({"answer": 42})), {"answer": 42})

    def test_payload_signature_valid(self):
        payload = {"task_id": "t1", "task_data": "abc"}
        payload["signature"] = sign_payload(payload, SECRET)
        self.assertTrue(verify_payload(payload, SECRET))

    def test_payload_signature_tamper_detected(self):
        payload = {"task_id": "t1", "task_data": "abc"}
        payload["signature"] = sign_payload(payload, SECRET)
        payload["task_data"] = "changed"
        self.assertFalse(verify_payload(payload, SECRET))

    def test_invalid_base64_task_data(self):
        with self.assertRaises(TaskPayloadError):
            decode_task("not valid base64!!!")


if __name__ == "__main__":
    unittest.main()
