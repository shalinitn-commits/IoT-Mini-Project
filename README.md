# Smart Farming Mesh Network — Zero-Hardware Python Prototype

This project is a **software simulation** of a solar-powered precision-farming mesh network.
It runs on a normal Windows/Linux computer and does not require ESP32, SX1278, sensors,
an antenna, a pump, or a physical solar panel.

## 1. Architecture

```text
Virtual Node 1 ─┐
                ├──> Virtual Relay Node 2 ───> Virtual Gateway ───> Blynk Cloud
Virtual Node 3 ─┘                                  │
Virtual Node 2 ────────────────────────────────────┘
                                                    └──> Local dashboard
```

Simulated routes:
- Node 1 -> Node 2 -> Gateway
- Node 3 -> Node 2 -> Gateway
- Node 2 -> Gateway

Only the gateway/cloud connection is represented as internet connectivity. The sensor
nodes do not connect to Wi-Fi in this model.

## 2. What is simulated?

- Three sensor nodes: soil moisture, temperature, humidity, light and battery.
- LoRa-like packet transport: configurable packet loss and retries.
- Mesh relay: forwarding, hop count, TTL and duplicate suppression.
- Gateway: receives packets and stores the latest telemetry per node.
- Irrigation: AUTO/MANUAL modes and moisture hysteresis.
- Solar/battery: light-dependent simulated charging and small simulated energy use.
- Blynk: optional HTTPS telemetry upload and remote control polling.
- Local dashboard: live browser view at `http://127.0.0.1:8000`.

**Important:** The program does not transmit LoRa packets. Packet loss, routing, RSSI-like
radio behavior and sensor readings are simulated. Irrigation status is not a real pump.

## 3. Requirements

- Python 3.9 or newer recommended.
- Internet connection only if you enable Blynk.
- No external Python packages are required.

Check Python:

```bash
python --version
```

## 4. Run on Windows

1. Extract the ZIP file.
2. Open the extracted `Smart_Farming_Mesh` folder.
3. Open Command Prompt or PowerShell in that folder.
4. Run:

```powershell
python main.py
```

If your system uses the Python launcher:

```powershell
py main.py
```

Open this address in your browser:

```text
http://127.0.0.1:8000
```

Stop with `Ctrl+C`.

## 5. Run on Linux

```bash
cd Smart_Farming_Mesh
python3 main.py
```

Open `http://127.0.0.1:8000` in a browser. Stop with `Ctrl+C`.

## 6. Optional Blynk Cloud setup

If you do not want to create a Blynk account yet, skip this section. The local dashboard
works without Blynk.

1. Sign in at https://blynk.cloud/
2. Create a template named `Smart Farming Mesh Network`.
3. Choose ESP32 as the hardware label and WiFi as the connection type. This is only the
   Blynk template metadata; the Python prototype itself runs on your computer.
4. Create a device from the template, for example `Farm Gateway`.
5. Create the following Datastreams (Virtual Pin):

| Pin | Datastream name | Type | Suggested range |
|---|---|---|---|
| V0 | Node1_Moisture | Integer | 0–100 |
| V1 | Node1_Temperature | Double | 0–60 |
| V2 | Node1_Humidity | Double | 0–100 |
| V3 | Node2_Moisture | Integer | 0–100 |
| V4 | Node2_Temperature | Double | 0–60 |
| V5 | Node2_Humidity | Double | 0–100 |
| V6 | Node3_Moisture | Integer | 0–100 |
| V7 | Node3_Temperature | Double | 0–60 |
| V8 | Node3_Humidity | Double | 0–100 |
| V9 | Irrigation_Status | Integer | 0–1 |
| V10 | Battery_Level | Double | 0–100 |
| V11 | Packets_Received | Integer | 0–100000 |
| V12 | Irrigation_Mode | Integer | 0–1 |
| V13 | Manual_Irrigation | Integer | 0–1 |
| V14 | Dry_Threshold | Integer | 5–40 |

6. Add dashboard widgets linked to the corresponding datastreams.
7. In the device info, copy the device Auth Token. Keep it private.
8. Set the token as an environment variable before running the project.

PowerShell (current terminal only):

```powershell
$env:BLYNK_AUTH_TOKEN="PASTE_YOUR_DEVICE_TOKEN_HERE"
python main.py
```

Linux/macOS:

```bash
export BLYNK_AUTH_TOKEN="PASTE_YOUR_DEVICE_TOKEN_HERE"
python3 main.py
```

Do not paste your Auth Token into public GitHub repositories, screenshots, or chats.
If the token is exposed, regenerate it in Blynk.

### Blynk controls

- V12: `0` = AUTO, `1` = MANUAL
- V13: `0` = irrigation OFF, `1` = irrigation ON (used in MANUAL mode)
- V14: dry threshold in percent (5–40)

AUTO uses hysteresis: irrigation switches ON below the dry threshold and switches OFF
when average moisture reaches the dry threshold + 15 percentage points. Between those
values, the previous state is retained.

## 7. Packet format

The original 10-field CSV packet structure is retained:

```text
src,seq,hop,ttl,moisture,temp,hum,light,batt,irrig
```

Example:

```text
1,12,0,3,28.5,31.2,57.0,72.0,88.4,1
```

- `src`: source node ID
- `seq`: sequence number
- `hop`: number of relay hops already traversed
- `ttl`: remaining forwarding allowance
- `moisture`: simulated soil moisture percentage
- `temp`: simulated temperature in Celsius
- `hum`: simulated relative humidity percentage
- `light`: simulated light level percentage
- `batt`: simulated battery percentage
- `irrig`: local node irrigation flag

The relay checks `(src, seq)` to reject duplicates. It will not forward a packet whose TTL
is zero. A forwarded packet increments `hop` and decrements `ttl`.

## 8. Project folders

```text
Smart_Farming_Mesh/
├── nodes/                 # Virtual sensor node models
├── network/               # Packet format, routes and relay behavior
├── gateway/               # Gateway, irrigation and energy logic
├── cloud/                 # Optional Blynk HTTPS integration
├── dashboard/             # Local browser dashboard
├── config.py              # Central settings
├── main.py                # Starts the simulation
├── .env.example           # Example environment settings
├── requirements.txt       # No external dependencies
└── README.md
```

## 9. Common problems

**`python` is not recognized:** install Python 3 and enable “Add Python to PATH”, or try
`py main.py` on Windows / `python3 main.py` on Linux.

**Port 8000 is already in use:** set another port before starting:
PowerShell: `$env:DASHBOARD_PORT="8001"`
Linux: `export DASHBOARD_PORT=8001`

**Blynk values do not update:** check that all virtual-pin datastreams exist, the device is
online in Blynk, the token is correct, and the computer has internet access. Check the
terminal for `[Blynk]` errors. Blynk API behavior and account limits can change; consult
the current Blynk documentation if an endpoint response differs.

**No Blynk account/token:** run without one. The local dashboard is the primary working
demonstration and does not need internet.

## 10. What to show in your project demonstration

1. Start `python main.py`.
2. Open the local dashboard.
3. Show all three virtual sensor nodes updating.
4. Show the routes and hop count in the terminal/logs.
5. Explain packet loss, retry, TTL and duplicate detection.
6. Explain the AUTO/MANUAL irrigation logic.
7. Explain that battery percentage changes using simulated solar input.
8. If configured, show the same telemetry in Blynk.

## 11. Limitations and future physical implementation

This prototype validates software logic only. It does not prove LoRa range, antenna
performance, actual sensor accuracy, solar charging efficiency, battery safety, or pump
operation. A physical implementation would require suitable hardware, calibrated sensors,
proper power design and an antenna. Check the current Indian WPC rules and permitted
frequency/power conditions before transmitting with any LoRa radio.

## 12. Run the built-in tests

```bash
python -m unittest discover -s tests -v
```
