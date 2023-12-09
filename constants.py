TITLE = "AnnoImage"
VERSION = "v0.1"

BACKGROUND_COLOR = "#111111"
SURFACE_COLOR = "#222222"
BACKGROUND_COLOR2 = "#333333"
FOREGROUND_COLOR = "#ffffff"
PRIMARY_COLOR = "#D16666"
HOVER_COLOR = "#643030"

BUTTON_BACKGROUND = "#333333"
BUTTON_HOVER = "#444444"

TOOLBAR_ICON_SIZE = 18
RIGHT_MAXW = 200
LOGO_SIZE = 24


def hex_to_rgb(color):
    color = color.replace("#", "")
    rgb = []
    for i in (0, 2, 4):
        decimal = int(color[i : i + 2], 16)
        rgb.append(decimal)

    return tuple(rgb)
