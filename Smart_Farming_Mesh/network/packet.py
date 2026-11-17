"""Packet model. CSV serialization preserves the original ESP32 packet schema:
src,seq,hop,ttl,moisture,temp,hum,light,batt,irrig
"""
from dataclasses import dataclass, asdict
import csv
import io

@dataclass
class Packet:
    src: int
    seq: int
    hop: int
    ttl: int
    moisture: float
    temp: float
    hum: float
    light: float
    batt: float
    irrig: int

    def key(self):
        return (self.src, self.seq)

    def to_csv(self):
        values = [
            self.src, self.seq, self.hop, self.ttl,
            round(self.moisture, 2), round(self.temp, 2),
            round(self.hum, 2), round(self.light, 2),
            round(self.batt, 2), self.irrig
        ]
        return ",".join(str(v) for v in values)

    @classmethod
    def from_csv(cls, line):
        row = next(csv.reader(io.StringIO(line)))
        if len(row) != 10:
            raise ValueError(f"Expected 10 CSV fields, received {len(row)}")
        return cls(
            src=int(row[0]), seq=int(row[1]), hop=int(row[2]), ttl=int(row[3]),
            moisture=float(row[4]), temp=float(row[5]), hum=float(row[6]),
            light=float(row[7]), batt=float(row[8]), irrig=int(row[9])
        )

    def forwarded(self):
        """Return a new packet with one more hop and one less TTL."""
        return Packet(
            src=self.src, seq=self.seq, hop=self.hop + 1, ttl=self.ttl - 1,
            moisture=self.moisture, temp=self.temp, hum=self.hum,
            light=self.light, batt=self.batt, irrig=self.irrig
        )

    def to_dict(self):
        return asdict(self)
