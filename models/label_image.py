import os


class LabelImage:
    def __init__(self, image_id: int, path: str, labels: list):
        self.path = path
        self.filename = os.path.basename(path)
        self.labels = labels
        self.image_id = image_id
        self.saved = True

    def __repr__(self):
        return f"LabelImage({self.image_id}, {self.path}, {len(self.labels)} labels)"

