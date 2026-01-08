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
    "Nord": ("#2E3440", "#D8DEE9"),
    "Retro": ("#FF1493", "#00BFFF"),
    "Sunset": ("#FF4E50", "#F9D423"),
    "Ocean": ("#1CB5E0", "#000046"),
}


def resolve_palette(
    palette: Optional[str], custom_fg: Optional[str], custom_bg: Optional[str]
) -> Tuple[str, str]:
    """Return (fg, bg) hex colors for a given palette name or if 'Custom' is used."""
    if palette and palette != "Custom" and palette in PALETTES:
        return PALETTES[palette]
    # Fallback to custom or defaults
    fg = custom_fg or "#000000"
    bg = custom_bg or "#FFFFFF"
    
    # Ensure they start with #
    if isinstance(fg, str) and not fg.startswith("#") and len(fg) in (3, 6):
        fg = f"#{fg}"
    if isinstance(bg, str) and not bg.startswith("#") and len(bg) in (3, 6):
        bg = f"#{bg}"
        
    return fg, bg


def build_gradient_spec(use_gradient: bool, g_from: Optional[str], g_to: Optional[str]) -> Optional[Dict]:
    """Return a simple gradient spec dict or None."""
    if not use_gradient:
        return None
    a = g_from or "#000000"
    b = g_to or "#FFFFFF"
    return {"type": "linear", "colors": [a, b], "angle": 90}
