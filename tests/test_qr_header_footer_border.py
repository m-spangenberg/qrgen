import os
from PIL import Image, ImageColor

from qrgen.qr import generate_qr


def _rgb(color):
    return ImageColor.getrgb(color)


def test_header_footer_and_border_visible(tmp_path):
    out = os.path.join(str(tmp_path), "preview_hdr.png")
    # generate with header/footer and a red border
    generate_qr(
        "BEGIN:VCARD\nEND:VCARD",
        dest=out,
        size=200,
        border=12,
        border_color="#ff0000",
        header_text="HEADER",
        footer_text="FOOTER",
        header_font_size=20,
        footer_font_size=16,
    )

    img = Image.open(out).convert("RGBA")
    pixels = img.load()
    w, h = img.size

    border_rgb = _rgb("#ff0000")

    # Compute header height and paste offset as generate_qr does (padding = 8)
    padding = 8
    header_h = 20 + padding
    paste_y = 12 + header_h  # border (12) + header_h

    # Confirm header area has non-border pixels (text drawn)
    found_non_border = False
    for y in range(0, header_h + 2):
        for x in range(0, w):
            if pixels[x, y][:3] != border_rgb:
                found_non_border = True
                break
        if found_non_border:
            break

    assert found_non_border, "Header text not visible (no non-border pixels in header band)"

    # Check left border is not overwritten by QR fill (should not equal QR fill color)
    mid_y = paste_y + (200 // 2)
    left_border_pixel = pixels[2, mid_y][:3]
    fill_rgb = _rgb("#000000")
    assert left_border_pixel != fill_rgb, f"Left border pixel {left_border_pixel} unexpectedly equals QR fill color {fill_rgb}"


def test_qr_and_border_separate_corner_radii(tmp_path):
    out = os.path.join(str(tmp_path), "preview_corner.png")
    # create with sizable qr_corner_radius and small border_corner_radius
    generate_qr(
        "TESTDATA",
        dest=out,
        size=220,
        border=20,
        border_color="#00ff00",
        corner_radius=0,
        qr_corner_radius=30,
        border_corner_radius=6,
        header_text=None,
        footer_text=None,
    )

    img = Image.open(out).convert("RGBA")
    pixels = img.load()
    w, h = img.size

    border_rgb = _rgb("#00ff00")
    back_rgb = _rgb("#ffffff")

    b = 20

    # Outer corner (0,0) may be transparent if outer rounding applied; ensure inner corner differs
    inner_x = b + 2
    inner_y = b + 2
    inner_pixel = pixels[inner_x, inner_y][:3]

    # With QR-area rounding the inner corner exposes the canvas (border_color) underneath
    assert inner_pixel == border_rgb, f"Inner corner pixel {inner_pixel} != border rgb {border_rgb} (expected rounded QR exposing border)"

    # Left border near center should be border color
    mid_y = h // 2
    left_border_pixel = pixels[2, mid_y][:3]
    assert left_border_pixel == border_rgb, "Outer border color not present where expected"
