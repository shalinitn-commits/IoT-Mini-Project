"""Simulated controlled-flooding relay with TTL and duplicate suppression."""
from collections import deque
from network.packet import Packet

class MeshRelay:
    def __init__(self, node_id=2, seen_limit=256):
        self.node_id = node_id
        self.seen_limit = seen_limit
        self.seen = set()
        self.seen_order = deque()
        self.forwarded_count = 0
        self.duplicate_count = 0
        self.ttl_drop_count = 0

    def _remember(self, key):
        if key in self.seen:
            return False
        self.seen.add(key)
        self.seen_order.append(key)
        if len(self.seen_order) > self.seen_limit:
            old = self.seen_order.popleft()
            self.seen.discard(old)
        return True

    def receive(self, packet):
        """Return a forwarded packet, or None when duplicate/TTL prevents forwarding."""
        if not self._remember(packet.key()):
            self.duplicate_count += 1
            return None
        if packet.ttl <= 0:
            self.ttl_drop_count += 1
            return None
        self.forwarded_count += 1
        return packet.forwarded()
