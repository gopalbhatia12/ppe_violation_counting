from ultralytics import YOLO
model = YOLO("models/best.pt")
print("\n========= model class ========== ")
print(model.names)
print("\n========= class information =========")
for class_id, class_name in model.names.items():
    print(class_id , ":", class_name)