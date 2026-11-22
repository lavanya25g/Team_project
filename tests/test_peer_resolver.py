import unittest
from execution.peer_resolver import resolve_peer_endpoint, PeerResolutionError


class FakeDHT:
    def __init__(self, records):
        self.records = records

    def find_peer(self, peer_id):
        return self.records.get(peer_id)


class TestPeerResolver(unittest.TestCase):
    def test_resolve_host_port_string(self):
        dht = FakeDHT({"p1": "127.0.0.1:9999"})
        self.assertEqual(resolve_peer_endpoint(dht, "p1"), ("127.0.0.1", 9999))

    def test_resolve_current_ip_only_dht_format(self):
        dht = FakeDHT({"p1": "127.0.0.1"})
        self.assertEqual(resolve_peer_endpoint(dht, "p1", 9999), ("127.0.0.1", 9999))

    def test_resolve_dict_record(self):
        dht = FakeDHT({"p1": {"host": "localhost", "port": 8888}})
        self.assertEqual(resolve_peer_endpoint(dht, "p1"), ("localhost", 8888))

    def test_missing_peer(self):
        with self.assertRaises(PeerResolutionError):
            resolve_peer_endpoint(FakeDHT({}), "missing", 9999)

    def test_missing_port(self):
        with self.assertRaises(PeerResolutionError):
            resolve_peer_endpoint(FakeDHT({"p1": "127.0.0.1"}), "p1")


if __name__ == "__main__":
    unittest.main()
