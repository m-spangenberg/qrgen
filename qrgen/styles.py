"""
styles.py: predefined palettes and helpers for resolving foreground/background
and gradients for QR generation.
"""
from typing import Dict, Optional, Tuple

PALETTES: Dict[str, Tuple[str, str]] = {
    "Classic": ("#000000", "#FFFFFF"),
    "Brand Blue": ("#1FA2D5", "#FFFFFF"),
    "Warm Sunset": ("#FF6B6B", "#FFF1E6"),
    "Forest": ("#0B8457", "#E8F6EF"),
    "Violet": ("#6A0DAD", "#F5E9FF"),
    "Slate": ("#0F172A", "#E6EEF6"),
}


def resolve_palette(palette: Optional[str], custom_fg: Optional[str], custom_bg: Optional[str]) -> Tuple[str, str]:
    """Return (fg, bg) hex colors for a given palette name or custom colors."""
    if palette and palette in PALETTES:
        return PALETTES[palette]
    # Fallback to custom or defaults
    fg = custom_fg or "#000000"
    bg = custom_bg or "#FFFFFF"
    return fg, bg


def build_gradient_spec(use_gradient: bool, g_from: Optional[str], g_to: Optional[str]) -> Optional[Dict]:
    """Return a simple gradient spec dict or None."""
    if not use_gradient:
        return None
    a = g_from or "#000000"
    b = g_to or "#FFFFFF"
    return {"type": "linear", "colors": [a, b], "angle": 90}
