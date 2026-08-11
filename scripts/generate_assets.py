from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "src" / "product_news" / "assets"


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if path and Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _draw_centered(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: str,
) -> None:
    left, top, right, bottom = box
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    x = left + (right - left - width) / 2 - bbox[0]
    y = top + (bottom - top - height) / 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=fill)


def make_icon() -> None:
    size = 1024
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for inset, color in [
        (46, "#25130d"),
        (66, "#7a1d11"),
        (86, "#f4c76d"),
        (112, "#fff4d7"),
    ]:
        draw.rounded_rectangle(
            (inset, inset, size - inset, size - inset),
            radius=220,
            fill=color,
        )

    # Baroque medallion ring.
    for angle in range(0, 360, 12):
        import math

        rad = math.radians(angle)
        cx = size / 2 + math.cos(rad) * 380
        cy = size / 2 + math.sin(rad) * 380
        draw.ellipse((cx - 18, cy - 18, cx + 18, cy + 18), fill="#b88a2c")

    # Cat head.
    draw.polygon([(315, 360), (392, 210), (462, 380)], fill="#2b160f")
    draw.polygon([(562, 380), (632, 210), (709, 360)], fill="#2b160f")
    draw.polygon([(344, 352), (394, 260), (438, 370)], fill="#f1b655")
    draw.polygon([(586, 370), (630, 260), (680, 352)], fill="#f1b655")
    draw.ellipse((250, 300, 774, 806), fill="#2b160f")
    draw.ellipse((288, 334, 736, 780), fill="#f6b85a")
    draw.ellipse((352, 450, 422, 520), fill="#2b160f")
    draw.ellipse((602, 450, 672, 520), fill="#2b160f")
    draw.ellipse((374, 468, 394, 488), fill="#fff8e7")
    draw.ellipse((624, 468, 644, 488), fill="#fff8e7")
    draw.polygon([(512, 536), (468, 584), (556, 584)], fill="#7a1d11")
    draw.arc((444, 562, 512, 632), 12, 130, fill="#7a1d11", width=10)
    draw.arc((512, 562, 580, 632), 50, 168, fill="#7a1d11", width=10)

    # Crown.
    draw.polygon(
        [(376, 324), (436, 210), (512, 306), (588, 210), (648, 324)],
        fill="#f7d36e",
    )
    draw.line([(376, 324), (648, 324)], fill="#7a1d11", width=18)
    for point in [(436, 210), (512, 306), (588, 210)]:
        x, y = point
        draw.ellipse((x - 22, y - 22, x + 22, y + 22), fill="#fff3b0")

    # Tiny badge. Keep this Latin-only so the icon is stable on CI font sets.
    draw.rounded_rectangle((346, 694, 678, 772), radius=39, fill="#7a1d11")
    _draw_centered(draw, (346, 694, 678, 772), "MEOW", _font(46, bold=True), "#fff8e7")

    # Depth pass.
    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((86, 116, 938, 970), radius=220, fill=(43, 22, 15, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(30))
    composed = Image.alpha_composite(shadow, img)
    composed.save(ASSET_DIR / "product_meow_icon.png")

    tray = composed.resize((256, 256), Image.Resampling.LANCZOS)
    tray.save(ASSET_DIR / "product_meow_tray.png")


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    make_icon()


if __name__ == "__main__":
    main()
