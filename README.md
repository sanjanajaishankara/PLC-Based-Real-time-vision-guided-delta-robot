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

The system uses machine vision to detect circular objects from camera images. The detected object center is converted from pixel coordinates into robot workspace coordinates using calibration and coordinate transformation called affine transformation.

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



## Add hardware connection section

```markdown
## Hardware Connection

| Component | Connection / Role |
|---|---|
| Camera | Connected to Raspberry Pi through USB |
| Raspberry Pi 5 | Runs Python and OpenCV vision program |
| B&R PLC | Receives object coordinates through Modbus TCP/IP |
| Delta Robot | Executes motion commands from PLC |
| Vacuum Gripper | Used for object pick-and-place |
| Ethernet | Used for Raspberry Pi to PLC communication |


## Modbus Communication Mapping

| Register / Signal | Purpose |
|---|---|
| DI_TRIGGER | PLC trigger signal to start vision detection |
| DI_DONE | Signal indicating vision processing completed |
| HR_SEQ | Sequence / operation number |
| HR_OBJ_COUNT | Number of detected objects |
| HR_X | Object X coordinate |
| HR_Y | Object Y coordinate |

## Camera-to-Robot Calibration

The detected pixel coordinates are converted into robot workspace coordinates using an affine transformation matrix.

```text
Robot_X = a1 × Pixel_X + a2 × Pixel_Y + a3
Robot_Y = b1 × Pixel_X + b2 × Pixel_Y + b3

## Limitations

- Detection accuracy depends on lighting conditions.
- Calibration must be updated if the camera position changes.
- Tracking is limited to the defined robot workspace.
- Only circular objects are considered in the current implementation.
- Real-time performance depends on camera frame rate and communication delay.
