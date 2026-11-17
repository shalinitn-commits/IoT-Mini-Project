"""Factory for virtual sensor node 3."""
from nodes.sensor_node import SensorNode

def create_node():
    return SensorNode(3, seed=103)
