import unittest
from network.packet import Packet
from network.mesh_relay import MeshRelay
from gateway.irrigation import IrrigationController

class ProjectTests(unittest.TestCase):
    def test_packet_csv_round_trip(self):
        p = Packet(1, 7, 0, 3, 32.5, 29.1, 61.0, 75.0, 88.0, 0)
        q = Packet.from_csv(p.to_csv())
        self.assertEqual((p.src, p.seq, p.ttl), (q.src, q.seq, q.ttl))

    def test_relay_forward_and_duplicate(self):
        relay = MeshRelay()
        p = Packet(1, 1, 0, 3, 30, 25, 50, 60, 90, 0)
        forwarded = relay.receive(p)
        self.assertEqual(forwarded.hop, 1)
        self.assertEqual(forwarded.ttl, 2)
        self.assertIsNone(relay.receive(p))
        self.assertEqual(relay.duplicate_count, 1)

    def test_ttl_zero_dropped(self):
        relay = MeshRelay()
        p = Packet(1, 2, 0, 0, 30, 25, 50, 60, 90, 0)
        self.assertIsNone(relay.receive(p))
        self.assertEqual(relay.ttl_drop_count, 1)

    def test_irrigation_hysteresis(self):
        c = IrrigationController(dry_threshold=30, wet_threshold=45)
        self.assertEqual(c.decide([20, 25, 27]), 1)
        self.assertEqual(c.decide([35, 38, 40]), 1)
        self.assertEqual(c.decide([50, 55, 60]), 0)
        c.update_commands(mode=1, manual_state=1)
        self.assertEqual(c.decide([80, 80, 80]), 1)

if __name__ == "__main__":
    unittest.main()
