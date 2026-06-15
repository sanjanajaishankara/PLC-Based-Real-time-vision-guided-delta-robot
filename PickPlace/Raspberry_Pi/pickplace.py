import time
import cv2
import numpy as np
from collections import deque
from pymodbus.client.sync import ModbusTcpClient

# ============================================================
# PLC / MODBUS SETTINGS
# ============================================================
PLC_IP = "192.168.0.1"
PLC_PORT = 1502
UNIT_ID = 1

DI_DONE = 0
DI_TRIGGER = 1

HR_SEQ = 0
HR_OBJ_COUNT = 1
HR_X = 2
HR_Y = 3

MAX_OBJECTS = 4
POLL_SEC = 0.2

# ============================================================
# CAMERA / CALIBRATION SETTINGS
# ============================================================
AFFINE_M = np.array([
    [0.182583600,  0.054978889, -64.8206448],
    [-0.094802350, 0.104244040, -16.4726014]
], dtype=np.float64)

CAM_INDEX = 0
FRAME_W = 640
FRAME_H = 480

AVG_WINDOW = 15
STABLE_FRAMES = 10
PRINT_INTERVAL_SEC = 0.25
CAMERA_TIMEOUT_SEC = 3
SHOW_WINDOW = True

TARGET_DIAMETER_PX = 224
DIAMETER_TOLERANCE_PX = 10

MIN_RADIUS = int((TARGET_DIAMETER_PX - DIAMETER_TOLERANCE_PX) / 2)
MAX_RADIUS = int((TARGET_DIAMETER_PX + DIAMETER_TOLERANCE_PX) / 2)

STABLE_STD_LIMIT = 3.0


# ============================================================
# HELPERS
# ============================================================
def cam_to_robot(u, v):
    uv1 = np.array([u, v, 1.0], dtype=np.float64)
    xy = AFFINE_M @ uv1
    return float(xy[0]), float(xy[1])


def signed_to_u16(value):
    return int(value) & 0xFFFF


def buffer_stats_xy(xy_buffer):
    arr = np.array(xy_buffer, dtype=np.float64)
    mean = arr.mean(axis=0)
    std = arr.std(axis=0)
    return mean, std


def put_text(img, text, x, y):
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                0.55, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                0.55, (255, 255, 255), 1, cv2.LINE_AA)


def draw_crosshair(img, u, v, size=10):
    cv2.line(img, (u - size, v), (u + size, v), (0, 255, 255), 1)
    cv2.line(img, (u, v - size), (u, v + size), (0, 255, 255), 1)


def open_camera():
    cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        raise RuntimeError("Camera not opened. Try CAM_INDEX = 0, 1, or 2.")

    for _ in range(5):
        cap.read()

    return cap


def detect_matching_circles(frame_bgr):
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    gray_blurred = cv2.GaussianBlur(gray, (9, 9), 2)

    circles = cv2.HoughCircles(
        gray_blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=80,
        param1=120,
        param2=35,
        minRadius=MIN_RADIUS,
        maxRadius=MAX_RADIUS
    )

    if circles is None:
        return []

    circles = np.uint16(np.around(circles[0]))
    detected = []

    for c in circles:
        u = int(c[0])
        v = int(c[1])
        r = int(c[2])
        diameter = 2 * r

        if abs(diameter - TARGET_DIAMETER_PX) <= DIAMETER_TOLERANCE_PX:
            detected.append((u, v, r, diameter))

    detected.sort(key=lambda obj: obj[0])   # left to right
    return detected[:MAX_OBJECTS]


def get_one_locked_pick_from_camera():
    cap = open_camera()

    xy_buffer = deque(maxlen=AVG_WINDOW)
    stable_count = 0
    last_print_t = 0.0
    start_t = time.time()

    win = "Single Pick From N Objects"

    if SHOW_WINDOW:
        cv2.namedWindow(win)

    try:
        while True:
            if time.time() - start_t > CAMERA_TIMEOUT_SEC:
                print("Camera timeout: no object found")
                return 0, 0, 0

            ret, frame = cap.read()

            if not ret:
                time.sleep(0.02)
                continue

            display = frame.copy()
            circles = detect_matching_circles(frame)
            obj_count = len(circles)

            if obj_count == 0:
                xy_buffer.clear()
                stable_count = 0

                if SHOW_WINDOW:
                    put_text(display, "No valid object", 10, 30)
                    cv2.imshow(win, display)
                    cv2.waitKey(1)

                continue

            # select only one object for this cycle
            # left-most object selected
            u, v, r, diameter = circles[0]
            rx, ry = cam_to_robot(u, v)
            xy_buffer.append([rx, ry])

            for idx, (cu, cv, cr, cd) in enumerate(circles, start=1):
                color = (0, 255, 0) if idx == 1 else (255, 0, 0)
                cv2.circle(display, (cu, cv), cr, color, 2)
                cv2.circle(display, (cu, cv), 3, color, -1)
                draw_crosshair(display, cu, cv)
                put_text(display, f"Obj{idx} D={cd}px", cu - 40, cv - cr - 10)

            if len(xy_buffer) == AVG_WINDOW:
                mean_xy, std_xy = buffer_stats_xy(xy_buffer)

                avg_x = float(mean_xy[0])
                avg_y = float(mean_xy[1])
                std_x = float(std_xy[0])
                std_y = float(std_xy[1])

                if std_x <= STABLE_STD_LIMIT and std_y <= STABLE_STD_LIMIT:
                    stable_count += 1
                else:
                    stable_count = 0

                if time.time() - last_print_t >= PRINT_INTERVAL_SEC:
                    print(
                        f"N={obj_count}, selected X={avg_x:.2f}, Y={avg_y:.2f}, "
                        f"STD=({std_x:.2f}, {std_y:.2f})"
                    )
                    last_print_t = time.time()

                if stable_count >= STABLE_FRAMES:
                    lock_x = int(round(avg_x))
                    lock_y = int(round(avg_y))

                    print("")
                    print("=== LOCKED ONE PICK FROM N OBJECTS ===")
                    print(f"N remaining/detected = {obj_count}")
                    print(f"Selected pick X,Y = ({lock_x}, {lock_y})")
                    print("=====================================")
                    print("")

                    return obj_count, lock_x, lock_y

            if SHOW_WINDOW:
                put_text(display, f"Detected N={obj_count}", 10, FRAME_H - 60)
                put_text(display, "Selected object = green", 10, FRAME_H - 30)
                cv2.imshow(win, display)

                key = cv2.waitKey(1) & 0xFF
                if key == 27 or key == ord("q"):
                    return 0, 0, 0

    finally:
        cap.release()
        if SHOW_WINDOW:
            cv2.destroyAllWindows()


def send_one_pick_to_plc(client, seq, obj_count, x_value, y_value):
    # Write data first
    regs = [
        int(obj_count),
        signed_to_u16(x_value),
        signed_to_u16(y_value)
    ]

    rr = client.write_registers(HR_OBJ_COUNT, regs, slave=UNIT_ID)

    if rr.isError():
        print("Error writing ObjCount/X/Y")
        return False

    # Write sequence last
    rr = client.write_register(HR_SEQ, seq, slave=UNIT_ID)

    if rr.isError():
        print("Error writing SeqCounter")
        return False

    print(f"Sent to PLC: SEQ={seq}, N={obj_count}, X={x_value}, Y={y_value}")
    return True


def main():
    client = ModbusTcpClient(PLC_IP, port=PLC_PORT, timeout=3)

    if not client.connect():
        print("Failed to connect to PLC")
        raise SystemExit

    print(f"Connected to PLC at {PLC_IP}:{PLC_PORT}")

    seq = 0

    try:
        while True:
            print("Waiting for Trigger from PLC...")

            while True:
                rr = client.read_discrete_inputs(DI_TRIGGER, 1, slave=UNIT_ID)

                if not rr.isError() and rr.bits[0]:
                    print("Trigger received")
                    break

                time.sleep(POLL_SEC)

            obj_count, x_value, y_value = get_one_locked_pick_from_camera()

            seq = (seq + 1) % 65535

            ok = send_one_pick_to_plc(client, seq, obj_count, x_value, y_value)

            if not ok:
                time.sleep(1)
                continue

            print("Waiting for Done from PLC...")

            while True:
                rr = client.read_discrete_inputs(DI_DONE, 1, slave=UNIT_ID)

                if not rr.isError() and rr.bits[0]:
                    print("Done received")
                    break

                time.sleep(POLL_SEC)

            print("Waiting for PLC reset...")

            while True:
                rr = client.read_discrete_inputs(0, 2, slave=UNIT_ID)

                if not rr.isError():
                    done_val = rr.bits[0]
                    trigger_val = rr.bits[1]

                    if not done_val and not trigger_val:
                        print("PLC reset complete")
                        print("")
                        break

                time.sleep(POLL_SEC)

            time.sleep(0.3)

    except KeyboardInterrupt:
        print("Stopped by user")

    finally:
        client.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
