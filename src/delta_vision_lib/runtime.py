from .calibration import Calibration
from .plc import PLCClient
from .vision import VisionSystem

class DeltaVisionSystem:
    def __init__(self, plc_ip: str, plc_port: int = 502):
        self.calib = Calibration()
        self.plc = PLCClient(plc_ip, plc_port)
        self.vision = VisionSystem()
        self.running = False

    def start_once(self):
        """
        Single-cycle demo run:
        1) connect PLC
        2) read targets from vision
        3) convert to robot coordinates
        4) send pick commands
        """
        self.plc.connect()
        targets = self.vision.get_targets()
        for px, py in targets:
            x, y, z = self.calib.image_to_robot(px, py)
            self.plc.write_pick_command(x, y, z)

    def stop(self):
        self.running = False
        self.plc.disconnect()
