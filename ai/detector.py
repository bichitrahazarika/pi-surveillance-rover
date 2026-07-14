import cv2
import onnxruntime as ort
import numpy as np

from ai.labels import COCO_CLASSES
import telemetry

# ==========================
# AI Toggle
# ==========================

AI_ENABLED = False

MODEL_PATH = "models/yolov8n.onnx"

session = None

# Box/label color, BGR. (0, 176, 255) = the HUD's amber #ffb000,
# so detections match the interface theme. Old green: (0, 255, 0).
BOX_COLOR = (0, 176, 255)


def enable_ai():
    global AI_ENABLED
    AI_ENABLED = True


def disable_ai():
    global AI_ENABLED
    AI_ENABLED = False
    # AI off → no detections; don't leave a stale count on the HUD
    telemetry.set_objects(0)


def ai_status():
    return AI_ENABLED


# ==========================
# Load YOLO Model
# ==========================

def load_model():
    global session
    if session is None:
        print("Loading YOLOv8 model...")
        session = ort.InferenceSession(
            MODEL_PATH,
            providers=["CPUExecutionProvider"]
        )
        print("✓ YOLOv8 model loaded.")
    return session


# ==========================
# AI Detection
# ==========================

def detect(frame):
    if not AI_ENABLED:
        return frame

    session = load_model()

    h, w = frame.shape[:2]

    # Prepare image for YOLO
    img = cv2.resize(frame, (640, 640))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1))
    img = np.expand_dims(img, axis=0)

    # Run inference
    outputs = session.run(
        None,
        {"images": img}
    )

    predictions = outputs[0][0]

    boxes = []
    scores = []
    class_ids = []

    for i in range(predictions.shape[1]):
        x = predictions[0][i]
        y = predictions[1][i]
        bw = predictions[2][i]
        bh = predictions[3][i]

        class_scores = predictions[4:, i]
        class_id = np.argmax(class_scores)
        confidence = class_scores[class_id]

        if confidence < 0.5:
            continue

        x1 = int((x - bw / 2) * w / 640)
        y1 = int((y - bh / 2) * h / 640)
        box_w = int(bw * w / 640)
        box_h = int(bh * h / 640)

        boxes.append([x1, y1, box_w, box_h])
        scores.append(float(confidence))
        class_ids.append(class_id)

    indices = cv2.dnn.NMSBoxes(
        boxes,
        scores,
        0.5,
        0.45
    )

    # Report how many objects survived NMS — the HUD polls this
    count = len(indices) if len(indices) > 0 else 0
    telemetry.set_objects(count)

    if count > 0:
        for i in indices.flatten():
            x, y, bw, bh = boxes[i]
            label = COCO_CLASSES[class_ids[i]]
            conf = scores[i]

            cv2.rectangle(
                frame,
                (x, y),
                (x + bw, y + bh),
                BOX_COLOR,
                2
            )
            cv2.putText(
                frame,
                f"{label} {conf:.2f}",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                BOX_COLOR,
                2
            )

    return frame
