import json
import os

from PIL import Image
from PySide6 import QtWidgets
from PySide6.QtCore import Qt, QPointF
from PySide6.QtWidgets import QProgressDialog, QGraphicsRectItem, QFileDialog

from models.label_image import LabelImage
from widgets.rectangle_item import RectangleItem


class AnnoProject:
    def __init__(
        self,
        main_window,
        name: str,
        images: list,
        class_names: list,
        dataset_type: str,
        path=None,
    ):
        self.main_window = main_window
        self.path = path
        self.name = name

        self.class_names = class_names
        self.dataset_type = dataset_type
        self.images = images

    def save_project(self):
        if not (self.path and self.path.endswith(".annoimg")):
            self.path = QFileDialog.getSaveFileName(
                self.main_window, "Save file", "", "*.annoimg"
            )[0]
            if not self.path:
                return

        json_data = {
            "name": self.name,
            "class_names": self.class_names,
            "dataset_type": self.dataset_type,
            "images": [image.to_dict() for image in self.images],
        }
        with open(self.path, "w") as file:
            json.dump(json_data, file)

    @classmethod
    def load(cls, path, main_window):
        with open(path, "r") as file:
            json_data = json.load(file)
            name = json_data.get("name")
            class_names = json_data.get("class_names")
            dataset_type = json_data.get("dataset_type")
            images = [
                LabelImage.from_dict(image_data)
                for image_data in json_data.get("images")
            ]
            return cls(main_window, name, images, class_names, dataset_type, path)

    # def load_labels(self, labels_path):
    #     progress_dialog = QProgressDialog(
    #         "Loading project...", "Cancel", 0, len(self.images), self.main_window
    #     )
    #     progress_dialog.setWindowModality(Qt.WindowModal)
    #     if self.dataset_type == "yolo":
    #         try:
    #             for index, image in enumerate(self.images):
    #                 if progress_dialog.wasCanceled():
    #                     break
    #
    #                 img = Image.open(image)
    #                 label_file = os.path.join(
    #                     labels_path, os.path.splitext(os.path.basename(image))[0] + ".txt"
    #                 )
    #                 labels = []
    #                 if os.path.exists(label_file):
    #                     with open(label_file, "r") as labels_file:
    #                         for line in labels_file.readlines():
    #                             line = line.strip()
    #                             label_id, x, y, w, h = line.split(" ")
    #                             x, y, width, height = (
    #                                 float(x) * img.width,
    #                                 float(y) * img.height,
    #                                 float(w) * img.width,
    #                                 float(h) * img.height,
    #                             )
    #                             label_name = self.class_names[int(label_id)]
    #
    #                             item = RectangleItem(
    #                                 QPointF(x - width / 2, y - height / 2),
    #                                 QPointF(x + width / 2, y + height / 2),
    #                                 label_name,
    #                                 label_id,
    #                                 img.width,
    #                                 img.height,
    #                                 self,
    #                             )
    #                             item.setFlag(QGraphicsRectItem.ItemIsMovable, True)
    #                             item.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
    #
    #                             labels.append(item)
    #
    #                 progress_dialog.setValue(index)
    #                 QtWidgets.QApplication.processEvents()
    #
    #                 self.images.append(LabelImage(index, image, labels))
    #
    #             progress_dialog.setValue(len(self.images_paths))
    #             QtWidgets.QApplication.processEvents()
    #
    #         finally:
    #             print(self.images)
    #             progress_dialog.close()
    #
    # elif self.dataset_type == "coco":
    #     labels_file_path = os.path.join(self.output_path)
    #     if os.path.exists(labels_file_path):
    #         with open(labels_file_path, "r") as labels_file:
    #             data = json.load(labels_file)
    #             self.coco_dataset = data

