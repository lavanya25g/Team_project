
from networking.protocol import (
    create_message,
    encode_message,
    decode_message
)

# Create a PING message
message = create_message(
    "node_01",
    "PING",
    {"message": "Hello MeshWeaver"}
)

# Convert message into bytes
encoded = encode_message(message)

# Convert bytes back into dictionary
decoded = decode_message(encoded)

# Display results
print("Original message:", message)
print("Encoded message:", encoded)
print("Decoded message:", decoded)

# Verify successful conversion
assert decoded == message

print("\nProtocol test passed!")
