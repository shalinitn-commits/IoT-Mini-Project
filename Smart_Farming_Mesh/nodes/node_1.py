"""Factory for virtual sensor node 1."""
from nodes.sensor_node import SensorNode

def create_node():
    return SensorNode(1, seed=101)
