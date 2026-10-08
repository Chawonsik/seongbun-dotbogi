"""Put the round-2 copy on the round-1 texture image. Same font, size, position and colour for A and B.

Font: Nanum Gothic (SIL Open Font License 1.1), the copy that ships with macOS.
Run from the repo root: python3 ads/r2/make_overlay.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ADS = Path(__file__).resolve().parents[1]
BASE_IMAGE = ADS / "r1" / "r1_B_texture_1x1.png"
FONT_PATH = (
    "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/"
    "7a0b5c0f3c1d41c4c52a33343496c9c65ad52c50.asset/AssetData/NanumGothic.ttc"
)
FONT_INDEX = 2  # ExtraBold
FONT_SIZE = 72
LINE_HEIGHT = 94
ORIGIN = (72, 72)
INK = (58, 42, 38)

COPIES = {
    "A_text_ingredient": ["PDRN 연어크림"],
    "B_text_review": ["바르면 쫀쫀해지고", "광이 나는 크림"],
}


def render(name: str, lines: list[str]) -> Path:
    image = Image.open(BASE_IMAGE).convert("RGB")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE, index=FONT_INDEX)
    x, y = ORIGIN
    for i, line in enumerate(lines):
        draw.text((x, y + i * LINE_HEIGHT), line, font=font, fill=INK)
    out = ADS / "r2" / f"r2_{name}_1x1.png"
    image.save(out)
    return out


if __name__ == "__main__":
    for name, lines in COPIES.items():
        print(render(name, lines))
