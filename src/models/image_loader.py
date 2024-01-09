from PIL import Image
from PIL.ImageQt import ImageQt
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QPixmap


class ImageLoader(QThread):
    loaded = Signal(object)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        self.image = Image.open(self.file_path)
        img = ImageQt(self.image)
        pixmap = QPixmap.fromImage(img)
        self.loaded.emit(pixmap)
