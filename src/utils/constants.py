TITLE = "AnnoImage"
DESCRIPTION = "An easy way to annotate images."
AUTHOR = "hawier-dev"
FULL_AUTHOR_NAME = "Mikołaj Badyl (hawier-dev)"
VERSION = "v0.1"
GITHUB_REPO_URL = "https://github.com/hawier-dev/annoimage"
ICON_PATH = "icons/logo.png"
BIG_LOGO_PATH = "icons/annoimage.png"

BACKGROUND_COLOR = "#111111"
SURFACE_COLOR = "#222222"
BACKGROUND_COLOR2 = "#333333"
BACKGROUND_COLOR3 = "#444444"
FOREGROUND_COLOR = "#ffffff"
PRIMARY_COLOR = "#605DF9"
SELECTED_COLOR = "#AEA0FF"
HOVER_COLOR = "#444444"
# HOVER_COLOR = "#4E4BEB"

BUTTON_BACKGROUND = "#333333"

TOOLBAR_ICON_SIZE = 18
RIGHT_MAXW = 300
LOGO_SIZE = 24


STYLESHEET = (
    "*:focus {outline: none;} "
    "* {font-family: Inter; font-size: 12px; color: white; border-radius: 5px;}"
    "QWidget {border: 0px solid black;} "
    "QLineEdit {height: 30px; padding-left: 10px; padding-right: 10px; background-color: "
    + f"{SURFACE_COLOR}"
    + "}"
    "QLineEdit:focus {border: 1px solid " + f"{BACKGROUND_COLOR2}" + "}"
    "QListWidget::item { height: 30px; background-color: "
    + f"{SURFACE_COLOR}"
    + "; margin: 1px;}"
    "QListWidget::item:hover { cursor: pointer; background-color: "
    + f"{BACKGROUND_COLOR2}"
    + ";}"
    "QListWidget::item:selected { background-color: "
    + f"{BACKGROUND_COLOR3}"
    + "; color: #ffffff;}"
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
    "QPushButton:hover {background-color: " + f"{HOVER_COLOR}" + ";}"
    "QPushButton:disabled {background-color: " + f"{SURFACE_COLOR}; color: #888" + "}"
    "QScrollBar:vertical {"
    "border: none;"
    f"background: {SURFACE_COLOR};"
    "width: 10px;"
    "margin: 0px 0px 0px 0px;"
    "border-radius: 5px;"
    "}"
    "QScrollBar::handle:vertical {"
    f"background: {BACKGROUND_COLOR2};"
    "min-height: 20px;"
    "border-radius: 5px;"
    "}"
    "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {"
    "height: 0px;"
    "background: none;"
    "}"
    "QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {"
    "background: none;"
    "}"
    "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {"
    "background: none;"
    "}"
    "QScrollBar:horizontal {"
    "border: none;"
    f"background: {SURFACE_COLOR};"
    "height: 10px;"
    "margin: 0px 0px 0px 0px;"
    "border-radius: 5px;"
    "}"
    "QScrollBar::handle:horizontal {"
    f"background: {BACKGROUND_COLOR2};"
    "min-width: 20px;"
    "border-radius: 5px;"
    "}"
    "QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {"
    "width: 0px;"
    "background: none;"
    "}"
    "QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {"
    "background: none;"
    "}"
    "QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {"
    "background: none;"
    "}"
    "QComboBox {"
    f"border: 1px solid {SURFACE_COLOR};"
    "border-radius: 5px;"
    "padding: 5px;"
    "margin: 2px;"
    "box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);"
    "}"
    "QComboBox:hover {background-color: " + f"{HOVER_COLOR}" + ";}"
    "QComboBox QAbstractItemView {background-color: "
    f"{SURFACE_COLOR}"
    "; padding: 5px;"
    "border-radius: 5px;"                                                           
    "box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); "                                                          
    "}"
    "QComboBox QAbstractItemView::item {padding: 5px;border-radius: 3px;}"
    "QComboBox QAbstractItemView::item:hover {background-color: " + f"{HOVER_COLOR}" + ";}"
    "QComboBox QAbstractItemView::item:selected {background-color: "
    + f"{PRIMARY_COLOR}"
    + "; color: #ffffff;}"
    "QComboBox::drop-down {border: none;}"
    "QComboBox::down-arrow {image: url(icons/arrow_down.png); width: 15px; height: 15px;}"
    "QComboBox QAbstractItemView QScrollBar:vertical {"
    "border: none;"
    "background: {SCROLLBAR_BACKGROUND_COLOR};"
    "width: 10px;"
    "}"
    "QComboBox QAbstractItemView QScrollBar::handle:vertical {"
    "background: {SCROLLBAR_HANDLE_COLOR};"
    "border-radius: 5px;"
    "}"
    "QComboBox QAbstractItemView QScrollBar::add-line:vertical,"
    "QComboBox QAbstractItemView QScrollBar::sub-line:vertical {"
    "border: none;"
    "background: none;"
    "}"
    "QTableWidget::item {background-color: " + f"{SURFACE_COLOR}" + ";}"
    "QTableWidget::item:selected {background-color: "
    + f"{PRIMARY_COLOR}"
    + "; color: #ffffff;}"
    "QTableWidget::item:focus {outline: none;}"
    "QHeaderView::section {background-color: "
    + f"{BACKGROUND_COLOR}"
    + "; color: #ffffff; border: none; padding: 5px;}"
    "QHeaderView::section:checked {background-color: " + f"{BACKGROUND_COLOR2}" + ";}"
    "QHeaderView::section:pressed {background-color: " + f"{BACKGROUND_COLOR2}" + ";}"
    "QHeaderView::section:checked:disabled {background-color: "
    + f"{BACKGROUND_COLOR2}"
    + ";}"
    "QTableCornerButton::section { background-color: " + f"{SURFACE_COLOR}" + ";}"
    "QMenu {background-color: " + f"{BACKGROUND_COLOR}" + ";}"
    "QMenu::item {background-color: "
    + f"{BACKGROUND_COLOR}"
    + "; color: #ffffff; padding: 5px;}"
    "QMenu::item:selected {background-color: " + f"{HOVER_COLOR}" + "; color: #ffffff;}"
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
    "QMenuBar {background-color: " + f"{SURFACE_COLOR}" + ";}"
    "QMenuBar::item {background-color: " + f"{SURFACE_COLOR}" + "; padding: 5px;}"
    "QMenuBar::item:selected {background-color: " + f"{HOVER_COLOR}" + ";}"
    "QMenuBar::item:pressed {background-color: " + f"{PRIMARY_COLOR}" + ";}"
    "QRadioButton {background-color: " + f"{BACKGROUND_COLOR}" + ";}"
    "QRadioButton::indicator {width: 15px; height: 15px;}"
    "QRadioButton::indicator:checked {"
    "background-color: " + f"{PRIMARY_COLOR}" + "; border-radius: 7px;"
    "}"
)


def hex_to_rgb(color):
    color = color.replace("#", "")
    rgb = []
    for i in (0, 2, 4):
        decimal = int(color[i : i + 2], 16)
        rgb.append(decimal)

    return tuple(rgb)
