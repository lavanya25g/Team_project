import unittest

from serialization import (
    serialize_function,
    deserialize_function,
    DeserializationError
)


# Normal function
def add(a, b):
    return a + b


# Closure function
def create_multiplier(factor):
    def multiply(number):
        return number * factor

    return multiply


# Function with default and keyword arguments
def calculate_total(price, quantity=1, discount=0):
    return (price * quantity) - discount


# Recursive function
def factorial(number):
    if number < 0:
        raise ValueError("Number must be non-negative")

    if number in (0, 1):
        return 1

    return number * factorial(number - 1)


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

    def test_recursive_function(self):
        serialized = serialize_function(factorial)
        restored = deserialize_function(serialized)

        self.assertEqual(restored(5), 120)
        self.assertEqual(restored(0), 1)
        self.assertEqual(restored(1), 1)

        with self.assertRaises(ValueError):
            restored(-1)

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