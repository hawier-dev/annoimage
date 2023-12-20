import os


class LabelImage:
    def __init__(self, image_id: int, path: str, labels: list):
        self.path = path
        self.name = os.path.basename(path)
        self.labels = labels
        self.image_id = image_id

    def __repr__(self):
        return f"LabelImage({self.image_id}, {self.path}, {len(self.labels)} labels)"

    def to_dict(self):
        return {
            "image_id": self.image_id,
            "path": self.path,
            "labels": self.labels,
        }

    @classmethod
    def from_dict(cls, label_dict: dict):
        return cls(label_dict["image_id"], label_dict["path"], label_dict["labels"])
