# Real-Time Vision-Guided Delta Robot

This project presents a real-time vision-guided robotic system for automated object detection, pick-and-place operation, and dynamic object tracking using a Delta Robot.

The system integrates:

- Raspberry Pi 5
- OpenCV
- B&R PLC
- Delta Robot
- Modbus TCP/IP communication
- Dual camera vision setup

The main objective of this project is to detect an object using computer vision, calculate its position, send the coordinates to the PLC, and execute robot motion for pick-and-place or tracking operation.

---

## Project Overview

The system uses machine vision to detect circular objects from camera images. The detected object center is converted from pixel coordinates into robot workspace coordinates using calibration and coordinate transformation.

The calculated coordinates are transferred from the Raspberry Pi to the B&R PLC through Modbus TCP/IP. Based on the received command and coordinates, the PLC controls the Delta Robot movement.

This project contains two main operating modes:

1. **Pick and Place**
2. **Dynamic Object Tracking**

---

## System Architecture

```text
Camera
  ↓
Raspberry Pi 5
  ↓
OpenCV Image Processing
  ↓
Object Detection and Coordinate Calculation
  ↓
Modbus TCP/IP Communication
  ↓
B&R PLC
  ↓
Delta Robot Motion Control
  ↓
Pick-and-Place / Tracking Operation
