import os
from qr_vcard.qr import generate_qr

def test_generate_qr_creates_file():
    test_path = "output/test_qr.png"
    generate_qr("test data", dest=test_path)
    assert os.path.isfile(test_path)
    os.remove(test_path)

def test_generate_qr_default():
    generate_qr("test data")
    assert os.path.isfile("output/preview.png")
    os.remove("output/preview.png")

def test_generate_qr_rgba_floats():
    rgba_color = "rgba(31.2774860619672, 162.69961539015245, 213.7514465332031, 1)"
    test_path = "output/test_qr_rgba.png"
    # This should not raise ValueError
    generate_qr("test data", dest=test_path, fill_color=rgba_color)
    assert os.path.isfile(test_path)
    os.remove(test_path)
