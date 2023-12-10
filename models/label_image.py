import os

from widgets.rectangle_item import RectangleItem


class LabelImage:
    def __init__(self, image_id: int, path: str, labels: list):
        self.path = path
        self.filename = os.path.basename(path)
        self.labels = labels
        self.image_id = image_id
        self.saved = True

    def __repr__(self):
        return f"LabelImage({self.image_id}, {self.path}, {len(self.labels)} labels)"

    def to_dict(self):
        return {
            "image_id": self.image_id,
            "path": self.path,
            "labels": [label.to_dict() for label in self.labels],
        }

    @classmethod
    def from_dict(cls, label_dict: dict):
        labels = [RectangleItem.from_dict(label) for label in label_dict["labels"]]
        return cls(label_dict["image_id"], label_dict["path"], labels)
