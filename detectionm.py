from torchvision.models import detection
from networkx.generators import spectral_graph_forge
from networkx.generators import spectral_graph_forge
from networkx.generators import spectral_graph_forge
from networkx.generators import spectral_graph_forge
# from sympy.multipledispatch.dispatcher import source
from ultralytics import YOLO

class pee_dection:
    def __init__(self , model_path= "models/best.pt"):
        self.model = YOLO(model_path)
    def detect_object(self, frame):
        results = self.model.predict(
            source = frame,
            conf = 0.35,
            verbose = False
        )
        detections = []

        # -- Boundary boxes
        for result in results:
            for box in result.boxes:
                x1 , y1, x2,y2 = map(int , box.xyxy[0].tolist()
                )
                class_id = int(box.cls[0])
                confidence= float(box.conf[0])

                class_name = self.model.names[class_id]
                class_name = str(class_name).lower().replace(" ", "_")
                detections.append({
                    "class": class_name,
                    "confidence" : confidence,
                    "box" :(x1,y1,x2,y2)
                })
        return detections
