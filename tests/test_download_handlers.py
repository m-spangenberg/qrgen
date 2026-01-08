import os
from qrgen.gui import _export_svg_preview, _download_batch


def test_export_svg_creates_file(tmp_path):
    out = _export_svg_preview()
    assert out is not None
    assert os.path.isfile(out)


def test_download_batch_creates_zip(tmp_path):
    z = _download_batch(None)
    assert z is not None
    assert os.path.isfile(z)
