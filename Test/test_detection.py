# from check_model import model
from torchvision.ops import boxes
from ultralytics import YOLO
import cv2
model = YOLO("models/best.pt")
cap = cv2.VideoCapture("Test/5434223-hd_1920_1080_24fps.mp4")
success , frame = cap.read()
cap.release()
if not success:
    print("Could not read")
    exit()
results = model.predict(
    source= frame,
    conf = 0.10,
    verbose = False
)
print("\n ========== Detection result ===========")
for result in results:
    if result.boxes is None:
        print("No object detected")
        continue
    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        class_name = model.names(class_id)
        print(
            "class:", class_name,
            "confidence:", round(confidence,3)
        )
cap.release()
