
import psutil
import time
from datetime import datetime, timezone


class ResourceMonitor:

    def __init__(self, node_id):
        self.node_id = node_id

    def get_resource_usage(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        resource_report = {
            "node_id": self.node_id,
            "cpu_usage": cpu_usage,
            "total_ram": round(memory.total / (1024 ** 2), 2),
            "used_ram": round(memory.used / (1024 ** 2), 2),
            "available_ram": round(memory.available / (1024 ** 2), 2),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        return resource_report

    def monitor(self, interval=5):
        print(f"Monitoring resources for {self.node_id}")

        try:
            while True:
                start_time = time.monotonic()

                report = self.get_resource_usage()

                print("\nResource Report:")
                for key, value in report.items():
                    print(f"{key}: {value}")

                elapsed = time.monotonic() - start_time
                time.sleep(max(0, interval - elapsed))

        except KeyboardInterrupt:
            print("\nResource monitoring stopped.")


if __name__ == "__main__":
    monitor = ResourceMonitor(node_id="node_01")
    monitor.monitor(interval=5)
