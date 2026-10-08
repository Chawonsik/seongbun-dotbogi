"""Render the round-2 ad images: the round-1 texture photo with an ivory label below it.

A and B share everything (photo, label, font, size, spacing, colours) except the copy.
The compared words (PDRN / 쫀쫀, 광) are set in bold and in the accent colour.

Font: Nanum Myeongjo (SIL Open Font License 1.1), the copy that ships with macOS.
Run from the repo root: python3 ads/r2/make_overlay.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ADS = Path(__file__).resolve().parents[1]
BASE_IMAGE = ADS / "r1" / "r1_B_texture_1x1.png"
FONT_PATH = (
    "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/"
    "4c932c71d74fc9e4c1bd9cbf270374b0b3ee7519.asset/AssetData/NanumMyeongjo.ttc"
)
FONT_INDEX_REGULAR = 0
FONT_INDEX_ACCENT = 2  # ExtraBold

CANVAS = 1080
PHOTO_SIZE = 900
LABEL_HEIGHT = 250
FONT_SIZE = 64
TRACKING = 6
LINE_HEIGHT = 98
EDGE_SAMPLE = 6

INK = (74, 58, 52)
ACCENT = (150, 92, 84)
LABEL = (244, 238, 229)
LABEL_RULE = (214, 203, 190)

# Each line is a list of (text, is_accent) pieces.
COPIES = {
    "A_text_ingredient": [[("PDRN", True), (" 연어크림", False)]],
    "B_text_review": [
        [("바르면 ", False), ("쫀쫀", True), ("해지고", False)],
        [("광", True), ("이 나는 크림", False)],
    ],
}


def photo_on_canvas() -> Image.Image:
    """Shrink the photo and keep it flush with the top and right edges so nothing in it is cut or faded.

    The empty strip on the left is filled by stretching the photo's own left edge, row by row,
    so the backdrop continues without a seam.
    """
    photo = Image.open(BASE_IMAGE).convert("RGB").resize((PHOTO_SIZE, PHOTO_SIZE))
    margin = CANVAS - PHOTO_SIZE
    canvas = Image.new("RGB", (CANVAS, CANVAS))
    edge = photo.crop((0, 0, EDGE_SAMPLE, PHOTO_SIZE)).resize((1, PHOTO_SIZE)).resize((margin, PHOTO_SIZE))
    canvas.paste(edge, (0, 0))
    canvas.paste(photo, (margin, 0))
    return canvas


def line_width(draw: ImageDraw.ImageDraw, pieces, regular, accent) -> float:
    width = 0.0
    for text, is_accent in pieces:
        font = accent if is_accent else regular
        for char in text:
            width += draw.textlength(char, font=font) + TRACKING
    return width - TRACKING


def draw_line(draw: ImageDraw.ImageDraw, x: float, y: float, pieces, regular, accent) -> None:
    for text, is_accent in pieces:
        font = accent if is_accent else regular
        for char in text:
            draw.text((x, y), char, font=font, fill=ACCENT if is_accent else INK)
            x += draw.textlength(char, font=font) + TRACKING


def render(name: str, lines) -> Path:
    image = photo_on_canvas()
    draw = ImageDraw.Draw(image)
    label_top = CANVAS - LABEL_HEIGHT
    draw.rectangle((0, label_top, CANVAS, CANVAS), fill=LABEL)
    draw.line((0, label_top, CANVAS, label_top), fill=LABEL_RULE, width=2)

    regular = ImageFont.truetype(FONT_PATH, FONT_SIZE, index=FONT_INDEX_REGULAR)
    accent = ImageFont.truetype(FONT_PATH, FONT_SIZE, index=FONT_INDEX_ACCENT)
    y = label_top + (LABEL_HEIGHT - LINE_HEIGHT * len(lines)) // 2 + 8
    for pieces in lines:
        x = (CANVAS - line_width(draw, pieces, regular, accent)) / 2
        draw_line(draw, x, y, pieces, regular, accent)
        y += LINE_HEIGHT

    out = ADS / "r2" / f"r2_{name}_1x1.png"
    image.save(out)
    return out


if __name__ == "__main__":
    for name, lines in COPIES.items():
        print(render(name, lines))
