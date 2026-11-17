"""Factory for virtual sensor node 2."""
from nodes.sensor_node import SensorNode

def create_node():
    return SensorNode(2, seed=102)
