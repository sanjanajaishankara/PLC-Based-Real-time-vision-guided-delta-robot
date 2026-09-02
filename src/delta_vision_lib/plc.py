class PLCClient:
    def __init__(self, ip: str, port: int = 502):
        self.ip = ip
        self.port = port
        self.connected = False

    def connect(self):
        # TODO: replace with actual PLC connection logic
        self.connected = True
        print(f"[PLC] Connected to {self.ip}:{self.port}")

    def disconnect(self):
        self.connected = False
        print("[PLC] Disconnected")

    def write_pick_command(self, x: float, y: float, z: float):
        if not self.connected:
            raise RuntimeError("PLC not connected")
        # TODO: replace with actual PLC register/tag writes
        print(f"[PLC] PICK -> X:{x:.2f}, Y:{y:.2f}, Z:{z:.2f}")
