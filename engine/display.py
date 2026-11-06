"""
Talks to the LED panel on the Pi, or to the browser emulator on your PC.
Same code runs in both places.
"""
from pathlib import Path

try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
    ON_PI = True
except ImportError:
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
    ON_PI = False

FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"
_fonts = {}
_colors = {}


def font(name):
    """font("5x7"), font("7x13"), etc. Every .bdf in fonts/ is available."""
    return _fonts[name]


def color(rgb):
    if rgb not in _colors:
        _colors[rgb] = graphics.Color(*rgb)
    return _colors[rgb]


def _load_fonts():
    for path in sorted(FONT_DIR.glob("*.bdf")):
        f = graphics.Font()
        f.LoadFont(str(path))
        _fonts[path.stem] = f


class Display:
    def __init__(self, panel):
        # Fonts load BEFORE the matrix starts. Starting the matrix as root
        # switches the program to a low-permission user that can't read
        # your home folder; that caused the "Permission denied: 7x13.bdf" crash.
        _load_fonts()

        opts = RGBMatrixOptions()
        opts.rows = panel["rows"]
        opts.cols = panel["cols"]
        opts.hardware_mapping = panel["hardware_mapping"]
        opts.gpio_slowdown = panel["gpio_slowdown"]
        opts.brightness = panel["brightness"]
        opts.drop_privileges = False   # belt and braces for the same problem

        self.matrix = RGBMatrix(options=opts)
        self.canvas = self.matrix.CreateFrameCanvas()
        self.width = panel["cols"]
        self.height = panel["rows"]

    def new_frame(self):
        self.canvas.Clear()
        return self.canvas

    def show(self):
        self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def clear(self):
        self.matrix.Clear()
