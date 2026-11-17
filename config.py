"""Central configuration for the zero-hardware smart farming mesh simulation."""
import os

# Simulation
SIMULATION_INTERVAL = float(os.getenv("SIMULATION_INTERVAL", "5"))
PACKET_LOSS_RATE = float(os.getenv("PACKET_LOSS_RATE", "0.08"))  # 0.0 to 1.0
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))
START_TTL = int(os.getenv("START_TTL", "3"))
BLYNK_UPLOAD_INTERVAL = float(os.getenv("BLYNK_UPLOAD_INTERVAL", "10"))
BLYNK_POLL_INTERVAL = float(os.getenv("BLYNK_POLL_INTERVAL", "5"))
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "127.0.0.1")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8000"))

# Blynk: add your device's Auth Token to .env or environment variables.
BLYNK_TOKEN = os.getenv("BLYNK_AUTH_TOKEN", "").strip()
BLYNK_BASE_URL = os.getenv("BLYNK_BASE_URL", "https://blynk.cloud")

# Fixed simulated topology:
# Node 1 -> Node 2 -> Gateway
# Node 3 -> Node 2 -> Gateway
# Node 2 -> Gateway
NODE_IDS = (1, 2, 3)
RELAY_NODE_ID = 2

# Blynk datastream virtual pin mapping
BLYNK_PINS = {
    "n1_moisture": "V0", "n1_temp": "V1", "n1_humidity": "V2",
    "n2_moisture": "V3", "n2_temp": "V4", "n2_humidity": "V5",
    "n3_moisture": "V6", "n3_temp": "V7", "n3_humidity": "V8",
    "irrigation_status": "V9", "battery_average": "V10",
    "packets_received": "V11", "irrigation_mode": "V12",
    "manual_irrigation": "V13", "dry_threshold": "V14",
}
