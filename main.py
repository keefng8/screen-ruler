"""Screen Ruler - measure anything on screen in pixels.

Two ways, because the two questions are different:

  * THE FRAME. The window itself is the ruler. Drag it over a button, an
    image, a margin, and read the size off it. Good for "how big is that".
  * TWO POINTS. Click anywhere, click again, and get the distance between
    them with the horizontal and vertical components. Good for "how far
    apart are those", which a frame cannot answer once the two things are
    not adjacent.

Deliberately very transparent, with a bright edge, so you can see what you
are measuring through it - that is the whole trick, and it is why this has
to be a window rather than a web page.

Standard library only.
"""
import ctypes
import math
import tkinter as tk

import mavis_ui as ui

FEATURE = "screen-ruler"
POLL_MS = 40

user32 = ctypes.windll.user32

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        user32.SetProcessDPIAware()
    except Exception:
        pass


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def cursor():
    point = POINT()
    user32.GetCursorPos(ctypes.byref(point))
    return point.x, point.y


# Ratios that everyone calls something other than their lowest terms. An
# ultrawide is 64:27 and nobody has ever said so out loud; they say 21:9.
COMMON_NAMES = {
    (64, 27): "21:9", (43, 18): "21:9", (12, 5): "12:5",
    (8, 5): "16:10", (32, 9): "32:9",
}


def gcd_ratio(w, h):
    """Aspect ratio in lowest terms, when that is a useful thing to say.

    16:9 is worth knowing. 1327:498 is not - it is noise dressed up as
    information - so anything that does not reduce to small numbers is
    reported as a decimal instead.

    The cutoff is 64 rather than something tidier because 64:27 is a real,
    common ratio: it is every ultrawide monitor, 2560x1080 and 3440x1440
    included. A tighter limit rejects it and prints "2.37:1", which is
    correct, useless, and looks like the tool does not know what it is
    looking at.
    """
    if not w or not h:
        return None
    divisor = math.gcd(w, h)
    rw, rh = w // divisor, h // divisor
    exact = "%d:%d" % (rw, rh)
    name = COMMON_NAMES.get((rw, rh))
    if name:
        # Only show both when they differ. 32:9 is already what people call
        # it, and "32:9 (32:9)" reads like a bug.
        return exact if name == exact else "%s (%s)" % (name, exact)
    if rw <= 64 and rh <= 64:
        return "%d:%d" % (rw, rh)
    return "%.2f:1" % (w / h)


class Ruler(ui.MavisWindow):
    def __init__(self):
        super().__init__(FEATURE, "Screen Ruler", width=520, height=300,
                         alpha=0.55, topmost=True)
        self.mode = "frame"
        self.first = None
        self.second = None
        self._was_down = False

        self._build()
        self._tick()

    def _build(self):
        # The readout bar is packed FIRST even though it sits at the bottom.
        # Tk's packer fills the cavity in packing order, so a canvas packed
        # before it with expand=True claims the whole thing and the bar never
        # appears at all.
        bar = tk.Frame(self.content, bg=ui.PANEL)
        bar.pack(fill="x", side="bottom")

        # The measuring area: a canvas with ticks drawn on it, mostly empty so
        # whatever is underneath shows through.
        self.canvas = tk.Canvas(self.content, bg=ui.INK, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.readout = tk.Label(bar, text="", bg=ui.PANEL, fg=ui.GLOW,
                                font=("Consolas", 11, "bold"))
        self.readout.pack(side="left", padx=12, pady=6)
        self.extra = tk.Label(bar, text="", bg=ui.PANEL, fg=ui.DIM,
                              font=("Consolas", 9))
        self.extra.pack(side="left")

        self.modebtn = ui.button(bar, "Measure two points", self.toggle_mode)
        self.modebtn.pack(side="right", padx=8, pady=4)

        self.canvas.bind("<Configure>", lambda e: self._draw_frame())

    # ------------------------------------------------------------------ frame
    def _draw_frame(self):
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 2 or height < 2:
            return

        # A bright inner edge, because the window is too transparent for its
        # own background to read as a boundary.
        self.canvas.create_rectangle(1, 1, width - 1, height - 1,
                                     outline=ui.GLOW, width=1)

        # Ticks every 10px, taller every 50, tallest every 100 - the same
        # convention as a real ruler, so it can be read at a glance.
        for x in range(0, width, 10):
            size = 4 if x % 50 else (8 if x % 100 else 13)
            self.canvas.create_line(x, 1, x, 1 + size, fill=ui.GLOW)
            self.canvas.create_line(x, height - 1, x, height - 1 - size, fill=ui.GLOW)
            if x and x % 100 == 0:
                self.canvas.create_text(x + 2, 16, text=str(x), anchor="w",
                                        fill=ui.TEXT, font=("Consolas", 7))
        for y in range(0, height, 10):
            size = 4 if y % 50 else (8 if y % 100 else 13)
            self.canvas.create_line(1, y, 1 + size, y, fill=ui.GLOW)
            self.canvas.create_line(width - 1, y, width - 1 - size, y, fill=ui.GLOW)
            if y and y % 100 == 0:
                self.canvas.create_text(4, y + 8, text=str(y), anchor="w",
                                        fill=ui.TEXT, font=("Consolas", 7))

        if self.mode == "frame":
            self.readout.configure(text="%d × %d px" % (width, height))
            ratio = gcd_ratio(width, height)
            self.extra.configure(
                text="   diagonal %d   %s" % (round(math.hypot(width, height)),
                                              ratio or ""))

    # ------------------------------------------------------------------ points
    def toggle_mode(self):
        self.mode = "points" if self.mode == "frame" else "frame"
        if self.mode == "points":
            self.first = self.second = None
            self._was_down = True     # ignore the click that pressed the button
            self.modebtn.configure(text="Measure the frame")
            self.readout.configure(text="click two points")
            self.extra.configure(text="   anywhere on screen — Escape cancels")
        else:
            self.modebtn.configure(text="Measure two points")
            self._draw_frame()

    def _tick(self):
        if self.mode == "points":
            down = bool(user32.GetAsyncKeyState(0x01) & 0x8000)
            if down and not self._was_down:
                point = cursor()
                if self.first is None or self.second is not None:
                    self.first, self.second = point, None
                    self.readout.configure(text="from %d,%d" % point)
                    self.extra.configure(text="   now click the second point")
                else:
                    self.second = point
                    self._report()
            self._was_down = down
        self.after(POLL_MS, self._tick)

    def _report(self):
        dx = self.second[0] - self.first[0]
        dy = self.second[1] - self.first[1]
        distance = math.hypot(dx, dy)
        self.readout.configure(text="%d px apart" % round(distance))
        angle = math.degrees(math.atan2(-dy, dx))
        self.extra.configure(
            text="   %d across, %d down   %.1f°" % (abs(dx), abs(dy), angle))
        self.clipboard_clear()
        self.clipboard_append(str(round(distance)))
        self.flash("copied %d" % round(distance))

    def on_close(self):
        return None


if __name__ == "__main__":
    Ruler().mainloop()
