import os
from qrgen.qr import generate_qr


def test_generate_qr_with_palette(tmp_path):
    dest = tmp_path / "out.png"
    generate_qr("Hello", dest=str(dest), size=120, palette="Brand Blue", shape="rounded", pattern="standard", error_correction="M")
    assert dest.exists() and dest.stat().st_size > 0


def test_generate_qr_with_gradient(tmp_path):
    dest = tmp_path / "out_grad.png"
    gradient = {"type": "linear", "colors": ["#1FA2D5", "#0A74B1"], "angle": 90}
    generate_qr("Gradient", dest=str(dest), size=120, gradient=gradient, shape="dot", error_correction="Q")
    assert dest.exists() and dest.stat().st_size > 0
