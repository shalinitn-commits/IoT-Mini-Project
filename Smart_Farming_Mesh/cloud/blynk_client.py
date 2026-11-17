
"""Blynk HTTPS External API client. No third-party Python package required."""

import urllib.parse
import urllib.request
import urllib.error
import json

from config import BLYNK_TOKEN, BLYNK_BASE_URL, BLYNK_PINS


class BlynkClient:

    def __init__(self, token=None, base_url=None, timeout=5):
        self.token = token if token is not None else BLYNK_TOKEN
        self.base_url = (base_url or BLYNK_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.enabled = bool(self.token)

    def _request(self, endpoint, params):
        if not self.enabled:
            print("[Blynk] Client is disabled. Check token.")
            return None

        params = dict(params)
        params["token"] = self.token

        url = (
            f"{self.base_url}/external/api/"
            f"{endpoint}?{urllib.parse.urlencode(params)}"
        )

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "SmartFarmingMesh/1.0"}
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                result = response.read().decode("utf-8").strip()
                return result

        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            print(f"[Blynk] {endpoint} failed: {exc}")
            return None

    def upload(self, values):
        """Upload multiple virtual pin values to Blynk."""

        if not self.enabled:
            return False

        params = {
            str(pin): value
            for pin, value in values.items()
        }

        result = self._request("batch/update", params)

        print("[Blynk] Upload values:", values)
        print("[Blynk] Response:", result)

        return result is not None

    def read_pin(self, pin):
        """Read a single virtual pin."""

        result = self._request("get", {"pin": pin})

        if result is None:
            return None

        try:
            parsed = json.loads(result)

            if isinstance(parsed, list) and parsed:
                return parsed[0]

            return parsed

        except (ValueError, TypeError):
            return result.strip().strip('"[]')

    def read_commands(self):
        """Read irrigation control commands from Blynk."""

        return {
            "mode": self.read_pin("V12"),
            "manual_state": self.read_pin("V13"),
            "dry_threshold": self.read_pin("V14"),
        }

    def upload_snapshot(self, snapshot, irrigation, packets_received):
        """Upload sensor data from all three mesh nodes."""

        nodes = snapshot.get("nodes", {})
        values = {}

        print("[Blynk] Available nodes:", list(nodes.keys()))

        # Upload sensor data from Node 1, Node 2 and Node 3
        for node_id in (1, 2, 3):

            state = nodes.get(str(node_id)) or nodes.get(node_id)

            if not state:
                print(f"[Blynk] Node {node_id} data not found.")
                continue

            base = (node_id - 1) * 3

            try:
                values[f"V{base}"] = round(
                    float(state["moisture"]), 2
                )

                values[f"V{base + 1}"] = round(
                    float(state["temp"]), 2
                )

                values[f"V{base + 2}"] = round(
                    float(state["hum"]), 2
                )

            except (KeyError, TypeError, ValueError) as exc:
                print(f"[Blynk] Node {node_id} invalid data: {exc}")

        # Calculate average battery level
        batteries = [
            float(state["batt"])
            for state in nodes.values()
            if isinstance(state, dict) and state.get("batt") is not None
        ]

        values["V9"] = int(irrigation.status)

        values["V10"] = (
            round(sum(batteries) / len(batteries), 2)
            if batteries else 0
        )

        values["V11"] = int(packets_received)
        values["V12"] = int(irrigation.mode)
        values["V13"] = int(irrigation.manual_state)
        values["V14"] = int(irrigation.dry_threshold)

        print("[Blynk] Final snapshot:", values)

        return self.upload(values)
