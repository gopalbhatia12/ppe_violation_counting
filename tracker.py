from ultralytics import YOLO
class PersonTracker:
    def __init__(self , model_path = "models/best.pt"):
        self.model= YOLO(model_path)
        self.unique_id= set()
        self.currnt_count= 0
    def track(self , frame):
        results = self.model.track(
            source = frame,
            persist = True,
            tracker = "bytetrack.yaml",
            conf = 0.35,
            verbose = False
        )
        people = []
        for result in results:
            if result.boxes is None:
                continue
            boxes = result.boxes

            for i in range(len(boxes)):
                class_id = int(boxes.cls[i])
                class_name = str(self.model.names[class_id]).lower().replace(" ","_")

                if class_name != "person":
                    continue
                if boxes.id is None : continue
                track_id = int(boxes.id[i])

                self.unique_id.add(track_id)

                people.append({
                    "id": track_id,
                    "box":boxes.xyxy[i].cpu().tolist()
                })
        self.currnt_count = len(people)
        return people, len(self.unique_id), self.currnt_count
        