
from ultralytics import YOLO

model = YOLO("models/best.pt")

results = model.predict(
    source="test.jpg",
    conf=0.35,
    save=True
)

print("Model test completed!")
print("Check the runs/detect folder.")
