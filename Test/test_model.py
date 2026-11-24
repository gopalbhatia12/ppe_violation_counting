from ultralytics import YOLO
model = YOLO("models/best.pt")

# Model Testing 
result = model.predict(
    source="test.jpg",
    conf = 0.25,
    save = True
)
print("Detection Completed")