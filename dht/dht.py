import hashlib


class DHT:

    def __init__(self):
        self.peers = {}

    def generate_peer_id(self, address):
        peer_id = hashlib.sha256(address.encode()).hexdigest()
        return peer_id[:12]

    def register_peer(self, address):

        if address in self.peers.values():
            print("Peer already registered!")
            return None

        peer_id = self.generate_peer_id(address)
        self.peers[peer_id] = address

        print("Peer registered:", peer_id)
        return peer_id

    def find_peer(self, peer_id):
        return self.peers.get(peer_id)

    def get_all_peers(self):
        return self.peers

    def remove_peer(self, peer_id):

        if peer_id in self.peers:
            del self.peers[peer_id]
            print("Peer removed successfully!")
            return True

        print("Peer not found!")
        return False