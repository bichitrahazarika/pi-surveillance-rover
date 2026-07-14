from ai.detector import (
    enable_ai,
    disable_ai,
    ai_status
)
from flask import Flask, render_template, Response, request, jsonify
from camera import get_frame
from motor import (
    forward,
    backward,
    left,
    right,
    stop,
    set_speed,
    get_speed
)
import telemetry
from config import FRAME_WIDTH, FRAME_HEIGHT

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


def generate_frames():
    while True:
        frame = get_frame()
        if frame is None:
            continue
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            frame +
            b'\r\n'
        )


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# ==========================
# Motor Control Routes
# ==========================

@app.route("/forward")
def move_forward():
    forward()
    return "OK"


@app.route("/backward")
def move_backward():
    backward()
    return "OK"


@app.route("/left")
def move_left():
    left()
    return "OK"


@app.route("/right")
def move_right():
    right()
    return "OK"


@app.route("/stop")
def move_stop():
    stop()
    return "OK"


# ==========================
# Speed Control
# ==========================

@app.route("/speed")
def speed():
    value = request.args.get("value")
    if value is not None:
        try:
            v = float(value)
        except ValueError:
            return "invalid value", 400
        # clamp to a sane PWM range so a bad request can't ask for 500%
        v = max(0.0, min(1.0, v))
        set_speed(v)
    return str(get_speed())


# ==========================
# AI Control
# ==========================

@app.route("/ai/on")
def ai_on():
    enable_ai()
    return "AI ON"


@app.route("/ai/off")
def ai_off():
    disable_ai()
    return "AI OFF"


@app.route("/ai/status")
def ai_state():
    return str(ai_status())


# ==========================
# Telemetry  (polled by the HUD once per second)
# ==========================

@app.route("/telemetry")
def get_telemetry():
    return jsonify(
        fps=round(telemetry.get_fps(), 1),
        objects=telemetry.get_objects(),
        resolution=f"{FRAME_WIDTH}x{FRAME_HEIGHT}",
        ai=bool(ai_status()),
    )


# ==========================
# Main
# ==========================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        threaded=True,
        debug=False
    )
# testing git
