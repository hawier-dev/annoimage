import os


class LabelImage:
    def __init__(self, image_id: int, path: str, labels: list, width: int, height: int):
        self.path = path
        self.name = os.path.basename(path)
        self.labels = labels
        self.image_id = image_id
        self.width = width
        self.height = height

    def __repr__(self):
        return f"LabelImage({self.image_id}, {self.path}, {len(self.labels)} labels)"

    def to_dict(self):
        return {
            "image_id": self.image_id,
            "path": self.path,
            "labels": self.labels,
            "width": self.width,
            "height": self.height,
        }

    @classmethod
    def from_dict(cls, label_dict: dict):
        return cls(
            label_dict["image_id"],
            label_dict["path"],
            label_dict["labels"],
            label_dict["width"],
            label_dict["height"],
        )
