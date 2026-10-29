"""Render the original profile artwork. Run with: uv run --with pillow scripts/render_mixtape.py

Fonts are local macOS fonts, or DejaVu Sans on Linux. Only rasterized artwork
is distributed; no font files or remote image services are needed by the README.
The GIF intentionally has no loop extension: it plays once and rests.
"""

from math import cos, sin, pi
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)
SCALE = 2
W, H = 1000, 360
INK = "#23364D"
PAPER = "#EAF0F7"
BLUE = "#AFCBE8"
PINK = "#E7A8B5"
YELLOW = "#F3D683"
WHITE = "#F9FBFE"


def font(size, bold=False):
    candidates = (
        ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
        if bold else
        ["/System/Library/Fonts/Supplemental/Arial.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    )
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size * SCALE)
    raise RuntimeError("Install Arial or DejaVu Sans to regenerate the artwork")


def render(phase):
    image = Image.new("RGB", (W * SCALE, H * SCALE), PAPER)
    d = ImageDraw.Draw(image)

    def box(bounds, fill, radius=0, outline=None, width=1):
        d.rounded_rectangle(tuple(int(v * SCALE) for v in bounds),
                            radius=radius * SCALE, fill=fill,
                            outline=outline, width=width * SCALE)

    def line(points, fill=INK, width=1):
        d.line([(int(x * SCALE), int(y * SCALE)) for x, y in points],
               fill=fill, width=width * SCALE)

    def text(x, y, value, size, fill=INK, bold=False):
        d.text((x * SCALE, y * SCALE), value, font=font(size, bold), fill=fill)

    # The title stays legible at profile width; supporting copy lives in Markdown.
    text(44, 38, "casafurix", 64, bold=True)
    text(48, 120, "apps that think.", 29)
    text(48, 158, "a few other things, too.", 29)
    line([(48, 224), (382, 224)], width=2)
    box((48, 248, 83, 283), PINK, radius=17)
    text(60, 253, "A", 19, bold=True)
    text(96, 254, "build / learn / repeat", 20)
    text(48, 309, "An Agnibha mixtape", 16)

    # A hand-drawn cassette, not a generic dashboard/stat card.
    box((453, 47, 956, 318), "#CED9E7", radius=24)
    box((443, 37, 946, 308), BLUE, radius=24, outline=INK, width=3)
    box((463, 57, 926, 240), WHITE, radius=12, outline=INK, width=2)
    box((464, 58, 925, 111), PINK, radius=11)
    box((464, 91, 925, 112), PINK)
    text(483, 70, "A", 24, bold=True)
    text(527, 74, "apps that think", 20, bold=True)
    text(842, 76, "C-90", 16)
    line([(464, 112), (925, 112)], width=2)

    # Tape window and two softly rotating spool spokes.
    box((493, 131, 896, 210), INK, radius=38)
    box((612, 151, 776, 190), "#617B96", radius=4)
    line([(620, 163), (768, 163)], BLUE, 2)
    line([(620, 179), (768, 179)], BLUE, 2)
    for cx in (552, 837):
        d.ellipse(((cx - 31) * SCALE, 140 * SCALE,
                   (cx + 31) * SCALE, 202 * SCALE), fill=WHITE)
        d.ellipse(((cx - 10) * SCALE, 161 * SCALE,
                   (cx + 10) * SCALE, 181 * SCALE), fill=INK)
        for spoke in range(6):
            angle = phase + spoke * pi / 3
            line([(cx + cos(angle) * 17, 171 + sin(angle) * 17),
                  (cx + cos(angle) * 27, 171 + sin(angle) * 27)], INK, 4)
    text(485, 217, "B   everything else", 15)
    box((733, 216, 906, 232), YELLOW, radius=3)
    # Cassette guide, screws, and an off-centre handwritten-feeling label.
    d.polygon([(int(x*SCALE), int(y*SCALE)) for x, y in
               [(568, 260), (821, 260), (842, 307), (547, 307)]], fill=PAPER)
    line([(547, 307), (568, 260), (821, 260), (842, 307)], INK, 2)
    for cx in (598, 791):
        d.ellipse(((cx-7)*SCALE, 277*SCALE, (cx+7)*SCALE, 291*SCALE), fill=INK)
    for cx, cy in ((459, 53), (930, 53), (459, 291), (930, 291)):
        line([(cx-3, cy), (cx+3, cy)], INK, 2)
        line([(cx, cy-3), (cx, cy+3)], INK, 2)
    text(691, 324, "made of curiosity", 16)
    return image.resize((W, H), Image.Resampling.LANCZOS)


if __name__ == "__main__":
    still = render(0)
    still.save(OUT / "mixtape.png", optimize=True)
    # One full turn in 4 seconds; last frame matches the static artwork.
    frames = [render(2 * pi * i / 40) for i in range(41)]
    palette = still.quantize(colors=96)
    frames = [frame.quantize(palette=palette) for frame in frames]
    frames[0].save(OUT / "mixtape.gif", save_all=True,
                   append_images=frames[1:], duration=100, optimize=True,
                   disposal=1)
    print("Rendered assets/mixtape.png and assets/mixtape.gif")
