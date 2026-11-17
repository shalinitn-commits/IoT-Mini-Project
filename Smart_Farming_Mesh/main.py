"""Run the complete Smart Farming Mesh software simulation."""
import random
import threading
import time
from config import (
    SIMULATION_INTERVAL, PACKET_LOSS_RATE, MAX_RETRIES,
    BLYNK_UPLOAD_INTERVAL, BLYNK_POLL_INTERVAL,
    DASHBOARD_HOST, DASHBOARD_PORT
)
from nodes.node_1 import create_node as create_node_1
from nodes.node_2 import create_node as create_node_2
from nodes.node_3 import create_node as create_node_3
from network.mesh_relay import MeshRelay
from network.routing import route_for
from gateway.gateway import Gateway
from gateway.irrigation import IrrigationController
from gateway.energy_manager import energy_summary
from cloud.blynk_client import BlynkClient
from dashboard.dashboard import DashboardServer

class SmartFarmingSimulation:
    def __init__(self):
        self.nodes = {
            1: create_node_1(),
            2: create_node_2(),
            3: create_node_3(),
        }
        self.relay = MeshRelay(node_id=2)
        self.gateway = Gateway()
        self.irrigation = IrrigationController()
        self.blynk = BlynkClient()
        self.running = False
        self.lock = threading.RLock()
        self.last_upload = 0
        self.last_poll = 0
        self.transmitted = 0
        self.delivered = 0
        self.lost = 0
        self.retry_count = 0
        self.rng = random.Random(2026)

    def _link_delivers(self):
        return self.rng.random() >= PACKET_LOSS_RATE

    def _try_link(self, packet, link_name):
        for attempt in range(MAX_RETRIES + 1):
            self.transmitted += 1
            if self._link_delivers():
                if attempt:
                    self.retry_count += attempt
                return True
            if attempt < MAX_RETRIES:
                print(f"[RADIO SIM] {link_name}: packet lost; retry {attempt+1}/{MAX_RETRIES}")
        self.lost += 1
        print(f"[RADIO SIM] {link_name}: packet dropped after retries")
        return False

    def _send_packet(self, packet):
        route = route_for(packet.src)
        if packet.src == 2:
            if self._try_link(packet, "Node 2 -> Gateway"):
                if self.gateway.receive(packet, route):
                    self.delivered += 1
            return

        # Sensor -> relay node 2.
        if not self._try_link(packet, f"Node {packet.src} -> Node 2"):
            return
        forwarded = self.relay.receive(packet)
        if forwarded is None:
            return

        # Relay -> gateway. The forwarded packet has hop=1 and ttl reduced by one.
        if not self._try_link(forwarded, "Node 2 -> Gateway"):
            return
        if self.gateway.receive(forwarded, route):
            self.delivered += 1

    def _poll_blynk(self):
        if not self.blynk.enabled:
            return
        now = time.time()
        if now - self.last_poll >= BLYNK_POLL_INTERVAL:
            self.last_poll = now
            commands = self.blynk.read_commands()
            with self.lock:
                self.irrigation.update_commands(
                    mode=commands.get("mode"),
                    manual_state=commands.get("manual_state"),
                    dry_threshold=commands.get("dry_threshold")
                )

    def _upload_blynk(self):
        if not self.blynk.enabled:
            return
        now = time.time()
        if now - self.last_upload >= BLYNK_UPLOAD_INTERVAL:
            self.last_upload = now
            with self.lock:
                snapshot = self.gateway.snapshot()
                irrigation_copy = self.irrigation
                count = self.gateway.packets_received
            self.blynk.upload_snapshot(snapshot, irrigation_copy, count)

    def dashboard_state(self):
        with self.lock:
            snap = self.gateway.snapshot()
            energy = energy_summary(snap["nodes"])
            return {
                **snap,
                "energy": energy,
                "irrigation": {
                    "status": self.irrigation.status,
                    "mode": self.irrigation.mode,
                    "manual_state": self.irrigation.manual_state,
                    "dry_threshold": self.irrigation.dry_threshold,
                    "wet_threshold": self.irrigation.wet_threshold,
                },
                "network": {
                    "transmitted_attempts": self.transmitted,
                    "delivered": self.delivered,
                    "lost_after_retries": self.lost,
                    "retry_count": self.retry_count,
                    "relay_forwarded": self.relay.forwarded_count,
                    "duplicates": self.relay.duplicate_count,
                    "ttl_drops": self.relay.ttl_drop_count,
                }
            }

    def run(self):
        self.running = True
        dashboard = DashboardServer(self, DASHBOARD_HOST, DASHBOARD_PORT)
        dashboard.start()
        print("[SYSTEM] Smart Farming Mesh simulation started.")
        print("[SYSTEM] Press Ctrl+C to stop.")
        if self.blynk.enabled:
            print("[BLYNK] Cloud integration enabled.")
        else:
            print("[BLYNK] No token found. Local dashboard mode only.")

        try:
            while self.running:
                with self.lock:
                    packets = [node.sample(
                        dry_threshold=self.irrigation.dry_threshold,
                        wet_threshold=self.irrigation.wet_threshold
                    ) for node in self.nodes.values()]
                    for packet in packets:
                        print(f"[NODE {packet.src}] TX {packet.to_csv()}")
                        self._send_packet(packet)

                    moisture = [
                        float(s["moisture"]) for s in self.gateway.nodes.values()
                    ]
                    self.irrigation.decide(moisture)

                self._poll_blynk()
                self._upload_blynk()
                time.sleep(SIMULATION_INTERVAL)
        except KeyboardInterrupt:
            print("\n[SYSTEM] Stopping simulation…")
        finally:
            self.running = False
            dashboard.stop()

if __name__ == "__main__":
    SmartFarmingSimulation().run()
