class VisionSystem:
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index

    def get_targets(self):
        """
        Return detected targets as list of (pixel_x, pixel_y).
        Replace with your OpenCV / ML detection pipeline.
        """
        return [(120, 80), (200, 150)]
