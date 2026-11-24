
import unittest
from datetime import datetime

from monitoring.resource_monitor import ResourceMonitor


class TestResourceMonitor(unittest.TestCase):

    def setUp(self):
        self.monitor = ResourceMonitor(node_id="test_node")

    def test_resource_report(self):
        report = self.monitor.get_resource_usage()

        # Check required fields
        self.assertIn("node_id", report)
        self.assertIn("cpu_usage", report)
        self.assertIn("total_ram", report)
        self.assertIn("used_ram", report)
        self.assertIn("available_ram", report)
        self.assertIn("timestamp", report)

        # Check node identity
        self.assertEqual(report["node_id"], "test_node")

        # Check CPU usage
        self.assertGreaterEqual(report["cpu_usage"], 0)
        self.assertLessEqual(report["cpu_usage"], 100)

        # Check RAM values
        self.assertGreater(report["total_ram"], 0)
        self.assertGreaterEqual(report["used_ram"], 0)
        self.assertGreaterEqual(report["available_ram"], 0)
        self.assertLessEqual(
            report["available_ram"], report["total_ram"]
        )

        # Check timestamp
        timestamp = datetime.fromisoformat(report["timestamp"])
        self.assertIsNotNone(timestamp)

    def test_node_id(self):
        monitor = ResourceMonitor("node_02")
        self.assertEqual(monitor.node_id, "node_02")


if __name__ == "__main__":
    unittest.main()
