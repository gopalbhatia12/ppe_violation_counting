from ultralytics import YOLO

model = YOLO("yolo11n.pt")

# Model training 
result = model.train(
    data = "dataset/construction-ppe-5e4e2603/data.yaml",
    epochs  = 50,
    imgsz = 640,
    batch = 8,
    project = "runs/ppe",
    name = "ppe_training"
)