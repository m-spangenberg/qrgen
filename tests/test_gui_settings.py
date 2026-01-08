from qrgen.i18n import t
import re


def test_i18n_keys_exist():
    assert t('save_settings') != 'save_settings'
    assert t('reset_settings') != 'reset_settings'
    assert t('settings_test_qr') != 'settings_test_qr'
    assert t('settings_saved') != 'settings_saved'
    assert t('ttf_suffix') != 'ttf_suffix'


def test_shared_logo_default_false_in_source():
    import pathlib
    p = pathlib.Path(__file__).parent.parent / 'qrgen' / 'gui.py'
    src = p.read_text()
    assert "shared_logo_enable = gr.Checkbox(label=t('enable_logo', lang), value=False)" in src


def test_save_reset_handlers_defined_in_source():
    import pathlib
    p = pathlib.Path(__file__).parent.parent / 'qrgen' / 'gui.py'
    src = p.read_text()
    assert 'def _save_settings' in src
    assert 'def _reset_to_defaults' in src
