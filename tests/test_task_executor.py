import unittest
from execution import execute_task, TaskExecutionError


def add(a, b):
    return a + b


def greet(name, prefix="Hello"):
    return f"{prefix}, {name}!"


def divide(a, b):
    return a / b


def get_status():
    return "Task completed"


class TestTaskExecutor(unittest.TestCase):
    def test_positional_arguments(self):
        self.assertEqual(execute_task(add, (10, 20)), 30)

    def test_keyword_arguments(self):
        self.assertEqual(execute_task(add, kwargs={"a": 5, "b": 15}), 20)

    def test_mixed_arguments(self):
        self.assertEqual(execute_task(add, (10,), {"b": 25}), 35)

    def test_default_arguments(self):
        self.assertEqual(execute_task(greet, ("Himanshu",)), "Hello, Himanshu!")

    def test_custom_keyword_argument(self):
        self.assertEqual(
            execute_task(greet, ("Himanshu",), {"prefix": "Welcome"}),
            "Welcome, Himanshu!",
        )

    def test_no_arguments(self):
        self.assertEqual(execute_task(get_status), "Task completed")

    def test_execution_error(self):
        with self.assertRaises(TaskExecutionError):
            execute_task(divide, (10, 0))

    def test_invalid_function(self):
        with self.assertRaises(TypeError):
            execute_task(100)

    def test_invalid_args_type(self):
        with self.assertRaises(TypeError):
            execute_task(add, [10, 20])

    def test_invalid_kwargs_type(self):
        with self.assertRaises(TypeError):
            execute_task(add, (10, 20), [("a", 10)])


if __name__ == "__main__":
    unittest.main()
