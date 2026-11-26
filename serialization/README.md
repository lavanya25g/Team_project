# ⚙️ Function Serialization Module

A Python function serialization and deserialization module built using **Cloudpickle**.

This module converts Python functions into byte data and restores them into callable Python objects, enabling function transfer and execution as part of the MeshWeaver project.

---

## 🛠️ Technologies Used

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Cloudpickle](https://img.shields.io/badge/Library-Cloudpickle-green)
![Testing](https://img.shields.io/badge/Testing-Unittest-orange)

---

## ✨ Features

- 🔄 Serialize Python functions into bytes.
- ♻️ Deserialize bytes back into callable Python objects.
- 🧩 Support for normal Python functions.
- ⚡ Support for lambda functions.
- 🔒 Support for closure functions.
- 🔁 Support for recursive functions.
- 🎯 Support for default and keyword arguments.
- 🔑 Support for keyword-only arguments.
- 📦 Support for variable-length arguments (`*args` and `**kwargs`).
- ⚠️ Custom exception handling.
- 🧪 Unit tests for different function types and invalid inputs.

---

## 📁 Project Structure

```text
serialization/
├── __init__.py
├── serializer.py
└── README.md

tests/
└── test_serializer.py

requirements.txt
```

---

## 🚀 Installation

**Step 1:** Clone the project repository:

```bash
git clone https://github.com/lavanya25g/Team_project.git
```

**Step 2:** Navigate to the project directory:

```bash
cd Team_project
```

**Step 3:** Install the required dependencies:

```bash
python -m pip install -r requirements.txt
```

---

## 💻 Usage

Import the serialization and deserialization functions:

```python
from serialization import serialize_function, deserialize_function

def add(a, b):
    return a + b

# Serialize the function
serialized_data = serialize_function(add)

# Deserialize the function
restored_function = deserialize_function(serialized_data)

# Execute the restored function
result = restored_function(10, 20)

print(result)  # Output: 30
```

**Expected Output:**

```text
30
```

---

## 📚 API Reference

### 1. `serialize_function(func)`

Serializes a callable Python object into bytes using Cloudpickle.

**Parameter:**
- `func`: A callable Python function.

**Returns:**
- Serialized function data in bytes format.

**Exceptions:**
- `TypeError`: If the input is not callable.
- `SerializationError`: If serialization fails.

### 2. `deserialize_function(data)`

Deserializes byte data back into a callable Python object.

**Parameter:**
- `data`: Serialized function data in bytes format.

**Returns:**
- A restored callable Python object.

**Exceptions:**
- `TypeError`: If the input is not bytes.
- `DeserializationError`: If deserialization fails or the restored object is not callable.

---

## 🧪 Running Tests

Run the following command from the project root directory:

```bash
python -m unittest discover -s tests -v
```

This command discovers and executes the unit tests inside the `tests` directory.

---

## ✅ Test Coverage

The module includes tests for:

| No. | Test Case | Description |
|---|---|---|
| 1 | Normal Function | Tests basic function serialization. |
| 2 | Lambda Function | Tests anonymous function serialization. |
| 3 | Closure Function | Tests functions with captured variables. |
| 4 | Default & Keyword Arguments | Tests default and named arguments. |
| 5 | Recursive Function | Tests recursive function serialization. |
| 6 | Variable-Length Arguments | Tests `*args` and `**kwargs`. |
| 7 | Keyword-Only Arguments | Tests keyword-only parameters. |
| 8 | Invalid Function | Tests non-callable input rejection. |
| 9 | Invalid Input Type | Tests invalid deserialization input types. |
| 10 | Invalid Serialized Data | Tests corrupted or invalid byte data. |
| 11 | Non-Callable Object | Tests rejection of restored non-callable objects. |

---

## ⚠️ Custom Exceptions

The module defines two custom exceptions:

- `SerializationError`: Raised when function serialization fails.
- `DeserializationError`: Raised when function deserialization fails or the restored object is not callable.

---

## 🔐 Security Warning

**Important:** Cloudpickle deserialization can execute arbitrary code.

- Only deserialize data received from trusted sources.
- Never deserialize untrusted or unauthenticated data.
- Remote task execution should only accept trusted and authorized peer payloads.

---

## 📌 Development Status

The function serialization and deserialization module has been implemented with support for different Python function types, argument patterns, custom exceptions, and unit testing.

Further integration with remote task transmission and execution is part of the subsequent project development.

---

<div align="center">

**🚀 MeshWeaver — Zero-Dependency P2P Async Task Broker**

*Function Serialization Module*

</div>

## Supported Function Types

The serializer supports regular functions, lambda functions, 
closures, recursive functions, and functions with default, 
keyword, and variable-length arguments.

Serialized functions should only be loaded from trusted 
sources because deserialization may execute arbitrary code.