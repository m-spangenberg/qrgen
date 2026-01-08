from qrgen.styles import resolve_palette, build_gradient_spec


def test_resolve_palette_known():
    fg, bg = resolve_palette("Brand Blue", None, None)
    assert fg.lower() == "#1fa2d5"
    assert bg.lower() == "#ffffff"


def test_build_gradient_spec():
    g = build_gradient_spec(True, "#ff0000", "#00ff00")
    assert isinstance(g, dict)
    assert g["type"] == "linear"
    assert g["colors"] == ["#ff0000", "#00ff00"]
