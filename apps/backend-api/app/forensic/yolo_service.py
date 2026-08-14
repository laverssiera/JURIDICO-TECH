from ultralytics import YOLO


class YoloForensicService:
    def __init__(self, model_name: str = "yolov8n.pt") -> None:
        self.model = YOLO(model_name)

    def detect(self, image_path: str):
        return self.model(image_path)
