BACKGROUND_COLOR = "#111111"
SURFACE_COLOR = "#222222"
FOREGROUND_COLOR = "#ffffff"
PRIMARY_COLOR = "#52528C"
HOVER_COLOR = "#231123"


def hex_to_rgb(color):
    color = color.replace("#", "")
    rgb = []
    for i in (0, 2, 4):
        decimal = int(color[i:i + 2], 16)
        rgb.append(decimal)

    return tuple(rgb)
