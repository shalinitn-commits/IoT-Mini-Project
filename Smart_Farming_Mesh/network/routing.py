"""Small deterministic routing table for the simulated mesh."""
from config import RELAY_NODE_ID

ROUTES = {
    1: [1, RELAY_NODE_ID, "GATEWAY"],
    2: [2, "GATEWAY"],
    3: [3, RELAY_NODE_ID, "GATEWAY"],
}

def route_for(node_id):
    return list(ROUTES.get(int(node_id), [int(node_id), "GATEWAY"]))
