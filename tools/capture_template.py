"""Tool chụp template image từ emulator.

Cách dùng:
    python tools/capture_template.py barb_icon

Sẽ chụp màn hình, mở lên cho bạn crop vùng cần lưu,
rồi save vào images/<tên>.png
"""
import sys
import os
import subprocess

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

roi = None
drawing = False
start_x, start_y = 0, 0


def mouse_callback(event, x, y, flags, param):
    global roi, drawing, start_x, start_y, img_copy

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_x, start_y = x, y
    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        img_copy = param.copy()
        cv2.rectangle(img_copy, (start_x, start_y), (x, y), (0, 255, 0), 2)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        roi = (min(start_x, x), min(start_y, y), max(start_x, x), max(start_y, y))


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/capture_template.py <template_name>")
        print("Example: python tools/capture_template.py barb_icon")
        sys.exit(1)

    name = sys.argv[1]
    address = f"{config.ADB_HOST}:{config.ADB_PORT}"

    print(f"Capturing screenshot from {address}...")
    proc = subprocess.run(
        ["adb", "-s", address, "exec-out", "screencap", "-p"],
        capture_output=True,
    )
    if not proc.stdout:
        print("Failed to capture. Is emulator running with ADB enabled?")
        sys.exit(1)

    img = cv2.imdecode(np.frombuffer(proc.stdout, np.uint8), cv2.IMREAD_COLOR)
    global img_copy
    img_copy = img.copy()

    print("Draw a rectangle around the element you want to save.")
    print("Press 's' to save, 'r' to retry, 'q' to quit.")

    cv2.namedWindow("Capture Template")
    cv2.setMouseCallback("Capture Template", mouse_callback, img)

    while True:
        cv2.imshow("Capture Template", img_copy)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("s") and roi:
            x1, y1, x2, y2 = roi
            cropped = img[y1:y2, x1:x2]
            os.makedirs(config.IMAGES_DIR, exist_ok=True)
            path = os.path.join(config.IMAGES_DIR, f"{name}.png")
            cv2.imwrite(path, cropped)
            print(f"Saved: {path} ({x2-x1}x{y2-y1})")
            break
        elif key == ord("r"):
            img_copy = img.copy()
            roi = None
        elif key == ord("q"):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
