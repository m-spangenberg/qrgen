import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from qrgen import i18n


def test_t_en():
    assert i18n.t('title', 'en') == 'QRGen'


def test_t_af():
    # Afrikaans should return its translation for generate_vcard
    assert i18n.t('generate_vcard', 'af').startswith('Genereer')


def test_t_es():
    # Spanish translations added — check a couple
    assert i18n.t('generate_vcard', 'es') == 'Generar vCard QR'
    assert i18n.t('qr_size', 'es').startswith('Tamaño')


def test_t_fallback_to_en():
    # If a key exists in English but not in the requested lang, fallback to English
    assert i18n.t('choose_format_instruction', 'es') == i18n.TRANSLATIONS['es']['choose_format_instruction']


def test_t_missing_key_returns_key():
    assert i18n.t('nonexistent_key_123', 'es') == 'nonexistent_key_123'


def test_localized_language_choices():
    choices, display_to_code, code_to_display = i18n.localized_language_choices('es')
    # Should contain entries for 'es', 'en', 'af'
    assert any('(es)' in c for c in choices)
    assert display_to_code[code_to_display['en']] == 'en'
    assert display_to_code[code_to_display['af']] == 'af'
