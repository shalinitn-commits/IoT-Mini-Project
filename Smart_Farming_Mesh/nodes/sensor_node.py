"""Virtual sensor node. Values are synthetic and are not physical sensor readings."""
import math
import random
from network.packet import Packet
from config import START_TTL

class SensorNode:
    def __init__(self, node_id, seed=None):
        self.node_id = node_id
        self.rng = random.Random(seed if seed is not None else node_id * 101)
        self.seq = 0
        self.moisture = self.rng.uniform(25, 65)
        self.temp = self.rng.uniform(24, 34)
        self.humidity = self.rng.uniform(40, 75)
        self.light = self.rng.uniform(25, 85)
        self.battery = self.rng.uniform(65, 95)
        self.local_irrigation = 0
        self.sample_count = 0

    def sample(self, dry_threshold=30, wet_threshold=45):
        # Slowly changing, bounded synthetic environment.
        self.sample_count += 1
        self.moisture = min(90, max(8, self.moisture + self.rng.uniform(-3.0, 2.0)))
        self.temp = min(42, max(15, self.temp + self.rng.uniform(-0.7, 0.7)))
        self.humidity = min(95, max(20, self.humidity + self.rng.uniform(-2.0, 2.0)))
        self.light = min(100, max(0, self.light + self.rng.uniform(-8, 8)))

        # Hysteresis: turn on below dry threshold; turn off at/above wet threshold.
        if self.moisture < dry_threshold:
            self.local_irrigation = 1
        elif self.moisture >= wet_threshold:
            self.local_irrigation = 0

        # Solar charging in brighter conditions; small simulated operating drain.
        solar_gain = max(0, self.light - 20) * 0.0018
        usage = 0.12
        self.battery = min(100, max(0, self.battery + solar_gain - usage))

        self.seq = (self.seq + 1) % 65536
        return Packet(
            src=self.node_id, seq=self.seq, hop=0, ttl=START_TTL,
            moisture=self.moisture, temp=self.temp, hum=self.humidity,
            light=self.light, batt=self.battery, irrig=self.local_irrigation
        )
