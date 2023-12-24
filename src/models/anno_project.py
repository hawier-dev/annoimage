import json
import os

from PIL import Image
from PySide6.QtWidgets import QFileDialog

from src.models.label_image import LabelImage
from src.widgets.labels.polygon_item import PolygonItem
from src.widgets.labels.rectangle_item import RectangleItem


class AnnoProject:
    def __init__(
        self,
        main_window,
        name: str,
        images: list,
        class_names: list,
        last_opened: str,
        path=None,
    ):
        self.main_window = main_window
        self.path = path
        self.name = name
        self.last_opened = last_opened

        self.class_names = class_names
        self.images = images
        self.saved = True
        self.current_image = None
        self.last_saved_state = None
        self.save_project()

    def save_project(self):
        """
        Save the project to a file.
        This function saves the project to a file with the extension ".annoimg".
        """

        if not (self.path and self.path.endswith(".annoimg")):
            self.path = QFileDialog.getSaveFileName(
                self.main_window, "Save file", "", "*.annoimg"
            )[0]
            if not self.path:
                return

        json_data = self.to_dict()
        with open(self.path, "w") as file:
            json.dump(json_data, file)

        self.last_saved_state = json_data

    @classmethod
    def load(cls, path, main_window):
        with open(path, "r") as file:
            json_data = json.load(file)
            name = json_data.get("name")
            class_names = json_data.get("class_names")
            last_opened = json_data.get("last_opened")
            images = [
                LabelImage.from_dict(image_data)
                for image_data in json_data.get("images")
            ]
            return cls(main_window, name, images, class_names, last_opened, path)

    @classmethod
    def create(cls, main_window, name, images, class_names, last_opened):
        label_images = []
        for i, image_path in enumerate(images):
            image = Image.open(image_path)
            label_image = LabelImage(
                image_id=i,
                labels=[],
                path=image_path,
                width=image.width,
                height=image.height,
            )
            label_images.append(label_image)

        return cls(
            main_window,
            name,
            label_images,
            class_names,
            last_opened,
            path=None,
        )

    def to_dict(self):
        return {
            "name": self.name,
            "class_names": self.class_names,
            "last_opened": self.last_opened,
            "images": [image.to_dict() for image in self.images],
        }

    def export_project(self, dataset_type, ignore_polygons, save_empty_files, save_path):
        """
        Export the project with the given settings.

        :param dataset_type: The type of dataset to export ('COCO' or 'YOLO').
        :param ignore_polygons: Whether to ignore polygons or convert them to rectangles.
        :param save_path: The directory path where the exported data will be saved.
        """
        if dataset_type == "COCO":
            self.export_to_coco(save_path)
        elif dataset_type == "YOLO":
            self.export_to_yolo(save_path, ignore_polygons, save_empty_files)

    def export_to_coco(self, save_path):
        coco_data = {
            "images": [],
            "annotations": [],
            "categories": [
                {"id": i, "name": name} for i, name in enumerate(self.class_names)
            ],
        }

        annotation_id = 1
        for img in self.images:
            coco_image = {
                "id": img.image_id,
                "file_name": img.name,
                "height": img.height,
                "width": img.width,
            }
            coco_data["images"].append(coco_image)

            for label_dict in img.labels:
                label = (
                    RectangleItem.from_dict(label_dict, self.main_window)
                    if label_dict["type"] == "RectangleItem"
                    else PolygonItem.from_dict(label_dict, self.main_window)
                )
                coco_annotation = label.to_coco_annotation()
                coco_annotation["image_id"] = img.image_id
                coco_annotation["id"] = annotation_id
                coco_data["annotations"].append(coco_annotation)

                annotation_id += 1

        with open(os.path.join(save_path, "annotations.json"), "w") as file:
            json.dump(coco_data, file, indent=4)

    def export_to_yolo(self, save_path, ignore_polygons, save_empty_files):
        for img in self.images:
            yolo_labels = []
            for label_dict in img.labels:
                label = (
                    RectangleItem.from_dict(label_dict, self.main_window)
                    if label_dict["type"] == "RectangleItem"
                    else PolygonItem.from_dict(label_dict, self.main_window)
                )
                if ignore_polygons and isinstance(label, PolygonItem):
                    continue
                elif isinstance(label, PolygonItem):
                    label = label.to_rectangle_item()

                yolo_label = label.to_yolo_label(img.width, img.height)
                yolo_labels.append(yolo_label)

            if not yolo_labels and not save_empty_files:
                continue

            with open(
                os.path.join(save_path, f"{os.path.splitext(img.name)[0]}.txt"), "w"
            ) as file:
                file.write("\n".join(yolo_labels))

    def get_current_image(self):
        for image in self.images:
            if image.image_id == self.current_image.image_id:
                return image
        return None

    def set_current_image(self, label_image):
        self.current_image = label_image

    def is_saved(self):
        current_state = self.to_dict()
        return self.last_saved_state == current_state
