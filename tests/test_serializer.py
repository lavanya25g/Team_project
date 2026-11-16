import unittest

from serialization import (
    serialize_function,
    deserialize_function,
    DeserializationError
)


def add(a, b):
    return a + b


def create_multiplier(factor):
    def multiply(number):
        return number * factor

    return multiply


def calculate_total(price, quantity=1, discount=0):
    return (price * quantity) - discount


class TestSerializer(unittest.TestCase):

    def test_normal_function(self):
        serialized = serialize_function(add)
        restored = deserialize_function(serialized)

        self.assertEqual(restored(10, 20), 30)

    def test_lambda_function(self):
        original = lambda x: x * 2

        serialized = serialize_function(original)
        restored = deserialize_function(serialized)

        self.assertEqual(restored(5), 10)

    def test_closure_function(self):
        original = create_multiplier(5)

        serialized = serialize_function(original)
        restored = deserialize_function(serialized)

        self.assertEqual(restored(4), 20)

    def test_default_and_keyword_arguments(self):
        serialized = serialize_function(calculate_total)
        restored = deserialize_function(serialized)

        self.assertEqual(restored(100), 100)

        self.assertEqual(
            restored(price=100, quantity=2, discount=20),
            180
        )

        self.assertIsInstance(serialized, bytes)

    def test_invalid_function(self):
        with self.assertRaises(TypeError):
            serialize_function(100)

    def test_invalid_input_type(self):
        with self.assertRaises(TypeError):
            deserialize_function("invalid data")

    def test_invalid_serialized_data(self):
        with self.assertRaises(DeserializationError):
            deserialize_function(b"invalid data")


if __name__ == "__main__":
    unittest.main()