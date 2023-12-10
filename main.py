import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QFontDatabase, QIcon
from PySide6.QtWidgets import QMainWindow, QWidget, QApplication
from app_gui import AppGui
from constants import *
from models.anno_project import AnnoProject
from widgets.new_project_widget import NewProjectWidget
from widgets.welcome_widget import WelcomeWidget
from widgets.yes_or_no_dialog import YesOrNoDialog


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(TITLE)
        self.setMinimumSize(600, 400)

        self.central_widget = QWidget()
        self.app_gui = None

        self.show_welcome_widget()
        # self.new_project()

    def new_project(self):
        new_project_widget = NewProjectWidget(self)
        new_project_widget.back_button.pressed.connect(self.show_welcome_widget)
        new_project_widget.project_created.connect(self.show_app_gui)

        self.setCentralWidget(new_project_widget)
        # anno_project = AnnoProject(
        #     self,
        #     class_names=[],
        #     images=[],
        #     output_path=[],
        #     dataset_type=None,
        # )
        # self.show_app_gui()

    def load_project(self):
        self.show_app_gui()

    def show_welcome_widget(self):
        welcome_widget = WelcomeWidget()
        welcome_widget.new_button.clicked.connect(self.new_project)
        welcome_widget.load_button.clicked.connect(self.load_project)

        self.setCentralWidget(welcome_widget)

    def show_app_gui(self, anno_project: AnnoProject):
        self.app_gui = AppGui(self)
        self.central_widget.setLayout(self.app_gui)
        self.setCentralWidget(self.central_widget)

    def closeEvent(self, event):
        if self.app_gui:
            saved = self.app_gui.saved
            if not saved:
                yes_no_dialog = YesOrNoDialog(
                    self,
                    window_title="Save changes?",
                    title="Save changes?",
                    text="You have unsaved changes. Do you want to save them?",
                    cancel=True,
                )
                result = yes_no_dialog.exec_()
                if result == YesOrNoDialog.Accepted:
                    self.app_gui.save_labels()
                elif result == YesOrNoDialog.Rejected and not yes_no_dialog.canceled:
                    self.close()
                else:
                    pass


def create_palette():
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


def main():
    app = QApplication()
    QFontDatabase.addApplicationFont("fonts/Inter-Medium.ttf")
    QFontDatabase.addApplicationFont("fonts/Inter-Bold.ttf")
    app.setPalette(create_palette())
    app.setWindowIcon(QIcon("icons/logo.ico"))
    app.setStyleSheet(
        "*:focus {outline: none;} "
        "* {font-family: Inter; font-size: 12px; color: white; border-radius: 5px;}"
        "QWidget {border: 0px solid black;} "
        "QLineEdit {height: 30px; padding-left: 10px; padding-right: 10px; background-color: "
        + f"{SURFACE_COLOR}"
        + "}"
        "QLineEdit:focus {border: 1px solid " + f"{BACKGROUND_COLOR2}" + "}"
        "QListWidget::item { height: 30px; background-color: #444; margin: 1px;}"
        "QListWidget::item:selected { background-color: #666; color: #ffffff;}"
        "QListWidget::item:focus {outline: none;}"
        "QToolBar {border: none; margin: 0px; padding: 0px; spacing: 0px;}"
        "QToolButton {background-color: "
        + f"{BACKGROUND_COLOR}"
        + "; border: none; color: #ffffff; padding: 10px; margin-bottom: 5px; margin-left:5px;}"
        "QToolButton:hover {background-color:" + f"{HOVER_COLOR}" + ";}"
        "QToolButton:checked {background-color: " + f"{PRIMARY_COLOR}" + ";}"
        "QToolButton:pressed {background-color: " + f"{PRIMARY_COLOR}" + ";}"
        "QPushButton {background-color: "
        + f"{BUTTON_BACKGROUND}"
        + "; border: none; color: #ffffff; padding: 10px;}"
        "QPushButton:hover {background-color: " + f"{BUTTON_HOVER}" + ";}"
        "QPushButton:disabled {background-color: "
        + f"{SURFACE_COLOR}; color: #888"
        + "}"
        "QScrollBar:vertical {border: none; background: "
        + f"{SURFACE_COLOR};"
        + " width: 18px; margin: 0px 0px 0px 0px;border-radius: 0px;}"
        "QScrollBar::handle:vertical {background: "
        + f"{BACKGROUND_COLOR2}"
        + "; min-height: 0px;}"
        "QScrollBar::add-line:vertical {background: "
        + f"{BACKGROUND_COLOR}"
        + "; height: 0px; subcontrol-position: bottom;}"
        "QScrollBar::sub-line:vertical {background: "
        + f"{BACKGROUND_COLOR}"
        + "; height: 0px; subcontrol-position: top;}"
        "QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {background: none;}"
        "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {background: none;}"
        "QScrollBar:horizontal {border: none; background: "
        + f"{SURFACE_COLOR};"
        + " height: 18px; margin: 0px 0px 0px 0px;border-radius: 0px;}"
        "QScrollBar::handle:horizontal {background: "
        + f"{BACKGROUND_COLOR2}"
        + "; min-width: 0px;}"
        "QScrollBar::add-line:horizontal {background: "
        + f"{BACKGROUND_COLOR}"
        + "; width: 0px; subcontrol-position: right;}"
        "QScrollBar::sub-line:horizontal {background: "
        + f"{BACKGROUND_COLOR}"
        + "; width: 0px; subcontrol-position: left;}"
        "QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {background: none;}"
        "QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {background: none;}"
        "QComboBox {border: 1px solid " + f"{SURFACE_COLOR}" + "; padding: 5px;}"
        "QComboBox:hover {background-color: " + f"{HOVER_COLOR}" + ";}"
        "QComboBox QAbstractItemView {background-color: "
        + f"{BACKGROUND_COLOR}"
        + "; padding: 10px;}"
        "QComboBox QAbstractItemView::item {height: 30px;}"
        "QComboBox QAbstractItemView::item:selected {background-color: "
        + f"{PRIMARY_COLOR}"
        + "; color: #ffffff;}"
        "QComboBox::drop-down {border: none;}"
        "QComboBox::down-arrow {image: url(icons/arrow_down.png); width: 15px; height: 15px;}"
        "QTableWidget::item {background-color: " + f"{SURFACE_COLOR}" + ";}"
        "QTableWidget::item:selected {background-color: "
        + f"{PRIMARY_COLOR}"
        + "; color: #ffffff;}"
        "QTableWidget::item:focus {outline: none;}"
        "QHeaderView::section {background-color: "
        + f"{BACKGROUND_COLOR}"
        + "; color: #ffffff; border: none; padding: 5px;}"
        "QHeaderView::section:checked {background-color: "
        + f"{BACKGROUND_COLOR2}"
        + ";}"
        "QHeaderView::section:pressed {background-color: "
        + f"{BACKGROUND_COLOR2}"
        + ";}"
        "QHeaderView::section:checked:disabled {background-color: "
        + f"{BACKGROUND_COLOR2}"
        + ";}"
        "QTableCornerButton::section { background-color: " + f"{SURFACE_COLOR}" + ";}"
        "QMenu {background-color: " + f"{BACKGROUND_COLOR}" + ";}"
        "QMenu::item {background-color: "
        + f"{BACKGROUND_COLOR}"
        + "; color: #ffffff; padding: 5px;}"
        "QMenu::item:selected {background-color: "
        + f"{PRIMARY_COLOR}"
        + "; color: #ffffff;}"
        "QMenu::item:pressed {background-color: "
        + f"{PRIMARY_COLOR}"
        + "; color: #ffffff;}"
        "QMenu::item:disabled {background-color: "
        + f"{BACKGROUND_COLOR}"
        + "; color: #ffffff;}"
        "QToolTip {background-color: "
        + f"{BACKGROUND_COLOR}"
        + "; color: #ffffff; border: none; padding: 5px;}"
        "QProgressBar {border: 1px solid "
        + f"{SURFACE_COLOR}"
        + ";  color: #ffffff; text-align: center;}"
        "QProgressBar::chunk {background-color: " + f"{PRIMARY_COLOR}" + ";}"
        "QMenuBar {background-color: " + f"{BACKGROUND_COLOR}" + ";}"
        "QMenuBar::item {background-color: " + f"{BACKGROUND_COLOR}" + ";}"
        "QMenuBar::item:selected {background-color: " + f"{PRIMARY_COLOR}" + ";}"
        "QMenuBar::item:pressed {background-color: " + f"{PRIMARY_COLOR}" + ";}"
    )
    window = MyApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
