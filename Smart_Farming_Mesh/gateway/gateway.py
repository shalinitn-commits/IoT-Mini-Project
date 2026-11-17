"""Gateway receives packets, rejects duplicates, stores latest node telemetry."""
from collections import deque
from network.packet import Packet

class Gateway:
    def __init__(self, seen_limit=512):
        self.seen = set()
        self.seen_order = deque()
        self.seen_limit = seen_limit
        self.nodes = {}
        self.packets_received = 0
        self.packet_log = deque(maxlen=100)
        self.routes = {}

    def receive(self, packet, route=None):
        key = packet.key()
        if key in self.seen:
            return False
        self.seen.add(key)
        self.seen_order.append(key)
        if len(self.seen_order) > self.seen_limit:
            self.seen.discard(self.seen_order.popleft())

        state = packet.to_dict()
        state["last_seen"] = __import__("time").time()
        state["status"] = "ONLINE"
        self.nodes[packet.src] = state
        self.routes[packet.src] = route or ["unknown", "GATEWAY"]
        self.packets_received += 1
        self.packet_log.append({
            "src": packet.src, "seq": packet.seq, "hop": packet.hop,
            "route": " -> ".join(str(x) for x in self.routes[packet.src]),
            "result": "delivered"
        })
        return True

    def snapshot(self):
        return {
            "nodes": {str(k): v for k, v in self.nodes.items()},
            "packets_received": self.packets_received,
            "packet_log": list(self.packet_log),
            "routes": {str(k): v for k, v in self.routes.items()}
        }
