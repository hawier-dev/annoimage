import json
import os
import sys

from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QPalette, QColor, QFontDatabase, QIcon
from PySide6.QtWidgets import QMainWindow, QWidget, QApplication, QFileDialog, QDialog
from appdirs import user_data_dir
from src.widgets.app_gui import AppGui
from src.utils.constants import *
from src.models.anno_project import AnnoProject
from src.widgets.dialogs.about_dialog import AboutDialog
from src.widgets.new_project_widget import NewProjectWidget
from src.widgets.welcome_widget import WelcomeWidget
from src.widgets.dialogs.yes_or_no_dialog import YesOrNoDialog


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = self.load_settings()

        self.setWindowTitle(TITLE)
        self.setMinimumSize(600, 400)

        self.central_widget = QWidget()
        self.app_gui = None

        self.show_welcome_widget()

    def new_project(
        self,
    ):
        new_project_widget = NewProjectWidget(self)
        new_project_widget.back_button.pressed.connect(self.show_welcome_widget)
        new_project_widget.project_created.connect(self.show_app_gui)

        self.setCentralWidget(new_project_widget)

    def load_project(self, path=None):
        if isinstance(path, QModelIndex):
            try:
                path = self.settings["last_projects"][path.row()]["path"]
            except IndexError or KeyError:
                return
        else:
            path, _ = QFileDialog.getOpenFileName(
                self,
                "Load Project",
                filter="Project Files (*.annoimg)",
            )

        if path:
            if not os.path.exists(path):
                delete_dialog = YesOrNoDialog(
                    self,
                    "File Not Found",
                    "File Not Found",
                    "The project you are trying to open does not exist.",
                    "Do you want to remove it from the list?",
                )
                result = delete_dialog.exec()
                if result == QDialog.Accepted:
                    for project in self.settings["last_projects"]:
                        if os.path.abspath(project["path"]) == os.path.abspath(path):
                            self.settings["last_projects"].remove(project)
                            self.save_settings()
                    self.show_welcome_widget()
            else:
                anno_project = AnnoProject.load(path, self)
                self.show_app_gui(anno_project)

    def show_welcome_widget(self):
        welcome_widget = WelcomeWidget(self.settings["last_projects"])
        welcome_widget.new_button.clicked.connect(self.new_project)
        welcome_widget.load_button.clicked.connect(self.load_project)
        welcome_widget.project_list.doubleClicked.connect(self.load_project)

        self.setCentralWidget(welcome_widget)

    def show_app_gui(self, anno_project: AnnoProject):
        for project in self.settings["last_projects"]:
            if os.path.abspath(project["path"]) == os.path.abspath(anno_project.path):
                self.settings["last_projects"].remove(project)

        self.settings["last_projects"].append(
            {
                "name": anno_project.name,
                "path": anno_project.path,
                "date_created": anno_project.date_created,
            }
        )
        self.save_settings()
        if self.settings["maximized"]:
            self.showMaximized()

        self.setWindowTitle(f"{TITLE} - {anno_project.name}")

        self.app_gui = AppGui(anno_project, self)
        self.central_widget.setLayout(self.app_gui)
        self.setCentralWidget(self.central_widget)

    def save_settings(self):
        settings_path = user_data_dir(TITLE, AUTHOR)
        os.makedirs(settings_path, exist_ok=True)
        settings_file = os.path.join(settings_path, "settings.json")
        with open(settings_file, "w") as f:
            json.dump(self.settings, f)

    def load_settings(self):
        settings_path = user_data_dir(TITLE, AUTHOR)
        os.makedirs(settings_path, exist_ok=True)
        settings_file = os.path.join(settings_path, "settings.json")
        settings = {"last_projects": [], "maximized": True}
        if os.path.exists(settings_file):
            with open(settings_file, "r") as f:
                settings = json.load(f)
        else:
            with open(settings_file, "w") as f:
                json.dump(settings, f)

        return settings

    def show_about_dialog(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    def closeEvent(self, event):
        self.settings["maximized"] = self.isMaximized()
        self.save_settings()


def setup_palette():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(*hex_to_rgb(BACKGROUND_COLOR)))
    palette.setColor(QPalette.WindowText, QColor(*hex_to_rgb(FOREGROUND_COLOR)))
    palette.setColor(QPalette.Base, QColor(*hex_to_rgb(SURFACE_COLOR)))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(*hex_to_rgb(PRIMARY_COLOR)))
    palette.setColor(QPalette.HighlightedText, Qt.black)

    return palette


def setup_fonts():
    QFontDatabase.addApplicationFont("fonts/Inter-Medium.ttf")
    QFontDatabase.addApplicationFont("fonts/Inter-Bold.ttf")


def main():
    app = QApplication()
    app.setApplicationName(TITLE)
    app.setApplicationVersion(VERSION)

    setup_fonts()
    app.setPalette(setup_palette())
    app.setWindowIcon(QIcon(ICON_PATH))
    app.setStyleSheet(STYLESHEET)

    window = MyApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
