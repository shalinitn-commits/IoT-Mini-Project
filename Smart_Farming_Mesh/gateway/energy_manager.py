"""Helpers for simulated solar/battery telemetry."""
def average_battery(node_states):
    values = [float(n["batt"]) for n in node_states.values() if n.get("batt") is not None]
    return round(sum(values) / len(values), 2) if values else 0.0

def energy_summary(node_states):
    return {
        "average_battery": average_battery(node_states),
        "low_battery_nodes": [
            node_id for node_id, state in node_states.items()
            if float(state.get("batt", 100)) < 20
        ]
    }
