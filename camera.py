from picamera2 import Picamera2
from config import *
import cv2

from ai.detector import detect
import telemetry

picam2 = Picamera2()

camera_config = picam2.create_video_configuration(
    main={
        "size": (FRAME_WIDTH, FRAME_HEIGHT),
        "format": "RGB888"
    }
)

picam2.configure(camera_config)
picam2.start()


def get_frame():
    frame = picam2.capture_array()

    # Frame captured — count it for the HUD FPS meter
    telemetry.record_frame()

    # Rotate if your camera is upside down
    # frame = cv2.rotate(frame, cv2.ROTATE_180)

    # AI processing
    frame = detect(frame)

    ret, buffer = cv2.imencode(".jpg", frame)
    if not ret:
        return None

    return buffer.tobytes()
