# Function Serialization Module

This module provides Python function serialization and deserialization
using the cloudpickle library.

## Features

- Serialize Python functions into bytes.
- Deserialize bytes back into callable Python objects.
- Supports normal functions, lambda functions and closures.
- Provides custom exception handling.
- Includes unit tests.

## Installation

From the project root directory, run:

```bash
python -m pip install -r requirements.txt
```

## Usage

```python
from serialization import serialize_function, deserialize_function

def add(a, b):
    return a + b

# Serialize function
serialized_data = serialize_function(add)

# Deserialize function
restored_function = deserialize_function(serialized_data)

# Execute restored function
result = restored_function(10, 20)

print(result)  # Output: 30
```

## Running Tests

From the project root directory:

```bash
python -m unittest discover -s tests -v
```

## Security Warning

Only deserialize data received from trusted sources.

Cloudpickle deserialization can execute arbitrary code.

Never deserialize untrusted data.