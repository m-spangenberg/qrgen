"""
qr.py: QR code generation utilities
"""

import os
import re

import qrcode
from PIL import Image, ImageColor


from typing import Optional, Union, Tuple

def _normalize_color(color: str) -> str:
    """
    Normalize color strings from Gradio (which might use rgba(r, g, b, a) with floats)
    to a hex format that both qrcode and Pillow understand.
    """
    if not isinstance(color, str):
        return color
    
    color_stripped = color.strip().lower()
    # If it's already a hex or a standard color name, return as is
    if not (color_stripped.startswith("rgba(") or color_stripped.startswith("rgb(")):
        return color

    try:
        # Extract all numeric parts
        nums = re.findall(r"[\d.]+", color_stripped)
        if len(nums) >= 3:
            r, g, b = [max(0, min(255, int(float(n)))) for n in nums[:3]]
            if len(nums) >= 4:
                a = float(nums[3])
                # Gradio often sends alpha in 0-1.0 range
                a_int = max(0, min(255, int(a * 255) if a <= 1.0 else int(a)))
                return f"#{r:02x}{g:02x}{b:02x}{a_int:02x}"
            return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        pass
        
    return color

def generate_qr(
    data: str,
    dest: str = "output/preview.png",
    size: int = 330,
    logo_path: str = None,
    fill_color: str = "black",
    back_color: str = "white",
) -> None:
    """
    Generate a QR code from the given data and save it to dest.
    Optionally overlay a logo image at the center if logo_path is provided.
    """
    if not os.path.exists(os.path.dirname(dest)):
        os.makedirs(os.path.dirname(dest))

    # Normalize colors for Pillow
    fill_color = _normalize_color(fill_color)
    back_color = _normalize_color(back_color)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Use high error correction for logo overlay
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")

    # Resize QR code
    try:
        resample = Image.Resampling.LANCZOS
    except AttributeError:
        resample = Image.LANCZOS
    img = img.resize((size, size), resample)

    # Overlay logo if provided
    if logo_path and os.path.isfile(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            # Calculate logo size (e.g., 20% of QR code size)
            logo_size = int(size * 0.2)
            logo = logo.resize((logo_size, logo_size), resample)
            # Calculate position
            pos = ((size - logo_size) // 2, (size - logo_size) // 2)
            # Paste logo with transparency mask
            img.paste(logo, pos, mask=logo)
        except Exception as e:
            print(f"Failed to overlay logo: {e}")

    img.save(dest)
