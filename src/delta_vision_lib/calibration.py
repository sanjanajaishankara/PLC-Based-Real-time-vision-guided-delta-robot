from dataclasses import dataclass

@dataclass
class Calibration:
    scale_x: float = 1.0
    scale_y: float = 1.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    z_pick: float = -200.0

    def image_to_robot(self, px: float, py: float):
        """
        Convert image pixel coordinates to robot XYZ coordinates.
        """
        x = px * self.scale_x + self.offset_x
        y = py * self.scale_y + self.offset_y
        z = self.z_pick
        return (x, y, z)
