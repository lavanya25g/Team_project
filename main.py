from dht.dht import DHT

# Create DHT network
network = DHT()

# Register peers
peer1 = network.register_peer("192.168.1.10")
peer2 = network.register_peer("192.168.1.11")
peer3 = network.register_peer("192.168.1.12")

# Display all peers
print("\nAll peers:")
print(network.get_all_peers())

# Search for peer2
print("\nSearching for peer2:")
print(network.find_peer(peer2))

# Test duplicate registration
print("\nTesting duplicate registration:")
network.register_peer("192.168.1.10")

# Remove peer2
print("\nRemoving peer2:")
network.remove_peer(peer2)

# Display updated peer list
print("\nUpdated peer list:")
print(network.get_all_peers())

# Search for removed peer
print("\nSearching for removed peer:")
print(network.find_peer(peer2))