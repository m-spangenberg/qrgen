"""
gui.py: GUI logic for QRGen
"""

import logging
import sys
import os
import shutil

import gradio as gr
import textwrap
import qrcode
import qrcode.image.svg

from .qr import generate_qr
from .i18n import t
from .validation import (
    validate_address,
    validate_birthday,
    validate_email,
    validate_note,
    validate_phone,
    validate_required,
    validate_url,
)
from .payloads import DEFAULT_VCARD_FIELDS, build_vcard


class QRGenGUI:
    def __init__(self):
        # All user-editable fields (exclude header/footer)
        header_footer = {"BEGIN", "VERSION", "KIND", "END"}
        self.user_fields = [k for k in DEFAULT_VCARD_FIELDS if k not in header_footer]
        self.field_descriptions = {
            "FN": "Full name of the contact. This is a required field.",
            "EMAIL;TYPE=WORK": "Work-related email address.",
            "EMAIL;TYPE=HOME": "Personal home email address.",
            "TITLE": "Job title or position.",
            "ROLE": "General role or department.",
            "BDAY": "Birthday in YYYYMMDD format (e.g., 19900101).",
            "ADR;TYPE=HOME": "Home address. Use ';' to separate parts: box;ext;street;city;region;zip;country",
            "TEL;TYPE=CELL": "Mobile or cell phone number.",
            "TEL;TYPE=WORK": "Office or work phone number.",
            "TEL;TYPE=HOME": "Personal home phone number.",
            "TEL;TYPE=FAX": "Fax number.",
            "URL": "Personal or company website URL.",
            "TZ": "IANA Timezone string (e.g., Africa/Windhoek or America/New_York).",
            "ORG": "Organization or Company name.",
            "NOTE": "A short personal note or comment (max 200 characters).",
        }

    def main(self):
        """
        Launch the Gradio interface for the QRGen.
        Sets up the layout, color pickers, logo upload, and preview area.
        """
        try:
            # New generators for each tab format
            def gen_vcard(*args):
                # args: [field1..N] + shared_inputs
                num = len(self.user_fields)
                vals = args[:num]
                # Map shared args into a dict by key to avoid fragile positional unpacking
                SHARED_KEYS = [
                    "shared_logo",
                    "shared_logo_enable",
                    "palette",
                    "transparent_bg",
                    "use_gradient",
                    "gradient_target",
                    "gradient_from",
                    "gradient_to",
                    "gradient_angle",
                    "custom_fg",
                    "custom_bg",
                    "shape",
                    "pattern",
                    "pattern_strength",
                    "logo_scale",
                    "logo_opacity",
                    "logo_clip",
                    "border",
                    "border_color",
                    "corner_radius",
                    "qr_corner_radius",
                    "header_text",
                    "footer_text",
                    "header_font_size",
                    "footer_font_size",
                    "header_font_select",
                    "header_font_file",
                    "header_bold",
                    "header_align",
                    "footer_font_select",
                    "footer_font_file",
                    "footer_bold",
                    "footer_align",
                    "size",
                    "ec",
                    "gradient_palette",
                ]
                shared_vals = args[num : num + len(SHARED_KEYS)]
                shared = dict(zip(SHARED_KEYS, shared_vals))
                # local aliases for readability
                logo_file = shared.get("shared_logo")
                logo_enable = shared.get("shared_logo_enable")
                palette = shared.get("palette")
                use_gradient = shared.get("use_gradient")
                gradient_target = shared.get("gradient_target")
                g_from = shared.get("gradient_from")
                g_to = shared.get("gradient_to")
                gradient_angle = shared.get("gradient_angle")
                custom_fg = shared.get("custom_fg")
                custom_bg = shared.get("custom_bg")
                shape = shared.get("shape")
                pattern = shared.get("pattern")
                pattern_strength = shared.get("pattern_strength")
                logo_scale = shared.get("logo_scale")
                logo_opacity = shared.get("logo_opacity")
                border = shared.get("border")
                border_color = shared.get("border_color")
                corner_radius = shared.get("corner_radius")
                qr_corner_radius = shared.get("qr_corner_radius")
                header_txt = shared.get("header_text")
                footer_txt = shared.get("footer_text")
                logo_clip = shared.get("logo_clip")
                logo_clip = shared.get("logo_clip")
                header_font_size = shared.get("header_font_size")
                footer_font_size = shared.get("footer_font_size")
                header_font_select_val = shared.get("header_font_select")
                header_font_file_val = shared.get("header_font_file")
                header_bold_val = shared.get("header_bold")
                header_align_val = shared.get("header_align")
                footer_font_select_val = shared.get("footer_font_select")
                footer_font_file_val = shared.get("footer_font_file")
                footer_bold_val = shared.get("footer_bold")
                footer_align_val = shared.get("footer_align")
                size = shared.get("size")
                ec = shared.get("ec")
                trans_bg = shared.get("transparent_bg")

                user_data = {
                    self.user_fields[i]: vals[i] for i in range(num) if vals[i]
                }

                validation_map = {
                    "FN": (validate_required, "Full Name is required."),
                    "EMAIL": (validate_email, "Invalid email format."),
                    "TEL": (validate_phone, "Invalid phone number format."),
                    "BDAY": (validate_birthday, "Birthday must be YYYYMMDD."),
                    "ADR": (
                        validate_address,
                        "Address needs at least 3 parts separated by ';'.",
                    ),
                    "URL": (validate_url, "Invalid URL format."),
                    "NOTE": (validate_note, "Note is too long (max 200 chars)."),
                }

                for field, value in user_data.items():
                    for key, (func, msg) in validation_map.items():
                        if key in field:
                            if not func(value):
                                return None, f"Error: {msg}"

                vcard_str = build_vcard(user_data)
                qr_content = (
                    vcard_str
                    if user_data
                    else "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                )
                logo_path = logo_file.name if logo_file and logo_enable else None
                # build gradient spec
                gradient = None
                if use_gradient:
                    if shared.get("gradient_palette") != "Custom":
                        from .styles import resolve_palette
                        pg_from, pg_to = resolve_palette(shared.get("gradient_palette"), None, None)
                    else:
                        pg_from, pg_to = g_from, g_to
                    gradient = {
                        "type": "linear",
                        "colors": [pg_from, pg_to],
                        "angle": int(gradient_angle)
                        if gradient_angle is not None
                        else 90,
                        "target": (gradient_target or "Background").lower(),
                    }

                # If palette is Custom, pass explicit colors, else pass palette string
                # wrap header/footer text to reasonable width so it doesn't overflow
                def _wrap_text(txt, fsize, sz):
                    if not txt:
                        return txt
                    try:
                        max_chars = max(
                            10, int((int(sz or 240) / max(8, int(fsize or 12))) * 1.8)
                        )
                    except Exception:
                        max_chars = 40
                    return "\n".join(textwrap.wrap(txt, width=max_chars))

                header_txt = _wrap_text(header_txt, header_font_size, size)
                footer_txt = _wrap_text(footer_txt, footer_font_size, size)

                if palette == "Custom":
                    fg = custom_fg
                    bg = custom_bg
                else:
                    fg = None
                    bg = None

                generate_qr(
                    qr_content,
                    logo_path=logo_path,
                    size=int(size) if size is not None else 240,
                    error_correction=ec,
                    shape=shape,
                    pattern=pattern,
                    palette=palette,
                    fill_color=fg,
                    back_color=bg,
                    transparent_bg=trans_bg,
                    gradient=gradient,
                    gradient_target=(gradient_target or "Background").lower(),
                    pattern_strength=int(pattern_strength)
                    if pattern_strength is not None
                    else 50,
                    logo_scale=logo_scale,
                    logo_opacity=logo_opacity,
                    logo_clip=logo_clip,
                    border=int(border) if border is not None else 0,
                    border_color=border_color,
                    corner_radius=int(corner_radius)
                    if corner_radius is not None
                    else 0,
                    qr_corner_radius=int(qr_corner_radius)
                    if qr_corner_radius is not None
                    else None,
                    border_corner_radius=int(corner_radius)
                    if corner_radius is not None
                    else None,
                    header_text=header_txt,
                    footer_text=footer_txt,
                    header_font_size=int(header_font_size)
                    if header_font_size is not None
                    else 16,
                    footer_font_size=int(footer_font_size)
                    if footer_font_size is not None
                    else 14,
                    header_font_path=(
                        header_font_file_val.name
                        if header_font_file_val
                        else (
                            header_font_select_val
                            if header_font_select_val != "Default"
                            else None
                        )
                    ),
                    footer_font_path=(
                        footer_font_file_val.name
                        if footer_font_file_val
                        else (
                            footer_font_select_val
                            if footer_font_select_val != "Default"
                            else None
                        )
                    ),
                    header_bold=bool(header_bold_val),
                    footer_bold=bool(footer_bold_val),
                    header_align=header_align_val,
                    footer_align=footer_align_val,
                )
                return "output/preview.png", qr_content
                return "output/preview.png", vcard_str, "vcard"

            def gen_generic(payload: str, *shared_args):
                # Map shared_args into a dict by key to avoid fragile positional unpacking
                SHARED_KEYS = [
                    "shared_logo",
                    "shared_logo_enable",
                    "palette",
                    "transparent_bg",
                    "use_gradient",
                    "gradient_target",
                    "gradient_from",
                    "gradient_to",
                    "gradient_angle",
                    "custom_fg",
                    "custom_bg",
                    "shape",
                    "pattern",
                    "pattern_strength",
                    "logo_scale",
                    "logo_opacity",
                    "logo_clip",
                    "border",
                    "border_color",
                    "corner_radius",
                    "qr_corner_radius",
                    "header_text",
                    "footer_text",
                    "header_font_size",
                    "footer_font_size",
                    "header_font_select",
                    "header_font_file",
                    "header_bold",
                    "header_align",
                    "footer_font_select",
                    "footer_font_file",
                    "footer_bold",
                    "footer_align",
                    "size",
                    "ec",
                    "gradient_palette",
                ]
                shared_vals = list(shared_args[: len(SHARED_KEYS)])
                # pad if shorter
                while len(shared_vals) < len(SHARED_KEYS):
                    shared_vals.append(None)
                shared = dict(zip(SHARED_KEYS, shared_vals))
                # local aliases for readability
                logo_file = shared.get("shared_logo")
                logo_enable = shared.get("shared_logo_enable")
                palette = shared.get("palette")
                use_gradient = shared.get("use_gradient")
                gradient_target = shared.get("gradient_target")
                g_from = shared.get("gradient_from")
                g_to = shared.get("gradient_to")
                gradient_angle = shared.get("gradient_angle")
                custom_fg = shared.get("custom_fg")
                custom_bg = shared.get("custom_bg")
                shape = shared.get("shape")
                pattern = shared.get("pattern")
                pattern_strength = shared.get("pattern_strength")
                logo_scale = shared.get("logo_scale")
                logo_opacity = shared.get("logo_opacity")
                border = shared.get("border")
                border_color = shared.get("border_color")
                corner_radius = shared.get("corner_radius")
                qr_corner_radius = shared.get("qr_corner_radius")
                header_txt = shared.get("header_text")
                footer_txt = shared.get("footer_text")
                header_font_size = shared.get("header_font_size")
                footer_font_size = shared.get("footer_font_size")
                header_font_select_val = shared.get("header_font_select")
                header_font_file_val = shared.get("header_font_file")
                header_bold_val = shared.get("header_bold")
                header_align_val = shared.get("header_align")
                footer_font_select_val = shared.get("footer_font_select")
                footer_font_file_val = shared.get("footer_font_file")
                footer_bold_val = shared.get("footer_bold")
                footer_align_val = shared.get("footer_align")
                size = shared.get("size")
                ec = shared.get("ec")
                trans_bg = shared.get("transparent_bg")

                payload = (payload or "").strip()
                if not payload:
                    return None, "Error: payload is empty"
                logo_path = (
                    logo_file.name
                    if getattr(logo_file, "name", None) and logo_enable
                    else None
                )
                gradient = None
                if use_gradient:
                    if shared.get("gradient_palette") != "Custom":
                        from .styles import resolve_palette
                        pg_from, pg_to = resolve_palette(shared.get("gradient_palette"), None, None)
                    else:
                        pg_from, pg_to = g_from, g_to
                    gradient = {
                        "type": "linear",
                        "colors": [pg_from, pg_to],
                        "angle": int(gradient_angle)
                        if gradient_angle is not None
                        else 90,
                        "target": (gradient_target or "Background").lower(),
                    }

                # wrap header/footer text
                def _wrap_text(txt, fsize, sz):
                    if not txt:
                        return txt
                    try:
                        max_chars = max(
                            10, int((int(sz or 240) / max(8, int(fsize or 12))) * 1.8)
                        )
                    except Exception:
                        max_chars = 40
                    return "\n".join(textwrap.wrap(txt, width=max_chars))

                header_txt = _wrap_text(header_txt, header_font_size, size)
                footer_txt = _wrap_text(footer_txt, footer_font_size, size)

                if palette == "Custom":
                    fg = custom_fg
                    bg = custom_bg
                else:
                    from .styles import resolve_palette
                    fg, bg = resolve_palette(palette, None, None)

                generate_qr(
                    payload,
                    logo_path=logo_path,
                    size=int(size) if size is not None else 240,
                    error_correction=ec,
                    shape=shape,
                    pattern=pattern,
                    fill_color=fg,
                    back_color=bg,
                    transparent_bg=trans_bg,
                    gradient=gradient,
                    gradient_target=(gradient_target or "Background").lower(),
                    pattern_strength=int(pattern_strength)
                    if pattern_strength is not None
                    else 50,
                    logo_scale=logo_scale,
                    logo_opacity=logo_opacity,
                    logo_clip=logo_clip,
                    border=int(border) if border is not None else 0,
                    border_color=border_color,
                    corner_radius=int(corner_radius)
                    if corner_radius is not None
                    else 0,
                    qr_corner_radius=int(qr_corner_radius)
                    if qr_corner_radius is not None
                    else None,
                    border_corner_radius=int(corner_radius)
                    if corner_radius is not None
                    else None,
                    header_text=header_txt,
                    footer_text=footer_txt,
                    header_font_size=int(header_font_size)
                    if header_font_size is not None
                    else 16,
                    footer_font_size=int(footer_font_size)
                    if footer_font_size is not None
                    else 14,
                    header_font_path=(
                        header_font_file_val.name
                        if header_font_file_val
                        else (
                            header_font_select_val
                            if header_font_select_val != "Default"
                            else None
                        )
                    ),
                    footer_font_path=(
                        footer_font_file_val.name
                        if footer_font_file_val
                        else (
                            footer_font_select_val
                            if footer_font_select_val != "Default"
                            else None
                        )
                    ),
                    header_bold=bool(header_bold_val),
                    footer_bold=bool(footer_bold_val),
                    header_align=header_align_val,
                    footer_align=footer_align_val,
                )
                return "output/preview.png", payload

            # Wrappers for each format — accept shared styling inputs in the defined order
            def gen_url(url, *shared_args):
                from .payloads import build_url

                res = gen_generic(build_url(url), *shared_args)
                if isinstance(res, tuple) and len(res) >= 2:
                    img, payload = res[0], res[1]
                    return img, payload
                return res

            def gen_text(text, *shared_args):
                from .payloads import build_text

                res = gen_generic(build_text(text), *shared_args)
                if isinstance(res, tuple) and len(res) >= 2:
                    img, payload = res[0], res[1]
                    return img, payload
                return res

            def gen_mailto(to, subject, body, *shared_args):
                from .payloads import build_mailto

                res = gen_generic(build_mailto(to, subject, body), *shared_args)
                if isinstance(res, tuple) and len(res) >= 2:
                    img, payload = res[0], res[1]
                    return img, payload
                return res

            def gen_tel(phone, *shared_args):
                from .payloads import build_tel

                res = gen_generic(build_tel(phone), *shared_args)
                if isinstance(res, tuple) and len(res) >= 2:
                    img, payload = res[0], res[1]
                    return img, payload
                return res

            def gen_sms(phone, msg, *shared_args):
                from .payloads import build_sms

                res = gen_generic(build_sms(phone, msg), *shared_args)
                if isinstance(res, tuple) and len(res) >= 2:
                    img, payload = res[0], res[1]
                    return img, payload
                return res

            def gen_wifi(ssid, auth, password, hidden, *shared_args):
                from .payloads import build_wifi

                res = gen_generic(
                    build_wifi(ssid, auth, password, hidden), *shared_args
                )
                if isinstance(res, tuple) and len(res) >= 2:
                    img, payload = res[0], res[1]
                    return img, payload
                return res

            def gen_geo(lat, lon, label, *shared_args):
                from .payloads import build_geo

                res = gen_generic(build_geo(lat, lon, label), *shared_args)
                if isinstance(res, tuple) and len(res) >= 2:
                    img, payload = res[0], res[1]
                    return img, payload
                return res

            def gen_event(summary, start, end, location, description, *shared_args):
                from .payloads import build_event

                res = gen_generic(
                    build_event(summary, start, end, location, description),
                    *shared_args,
                )
                if isinstance(res, tuple) and len(res) >= 2:
                    img, payload = res[0], res[1]
                    return img, payload
                return res

            def gen_applink(url, *shared_args):
                from .payloads import build_applink

                res = gen_generic(build_applink(url), *shared_args)
                if isinstance(res, tuple) and len(res) >= 2:
                    img, payload = res[0], res[1]
                    return img, payload
                return res

            def gen_payment(address, amount, label, *shared_args):
                from .payloads import build_payment

                res = gen_generic(build_payment(address, amount, label), *shared_args)
                if isinstance(res, tuple) and len(res) >= 2:
                    img, payload = res[0], res[1]
                    return img, payload
                return res

            def gen_mecard(name, tel, email, org, note, *shared_args):
                from .payloads import build_mecard

                res = gen_generic(
                    build_mecard(name, tel, email, org, note), *shared_args
                )
                if isinstance(res, tuple) and len(res) >= 2:
                    img, payload = res[0], res[1]
                    return img, payload
                return res

            def reset_inputs():
                # Returns: resets for inputs + color pickers + output image + preview text
                return (
                    [None] * (len(self.user_fields) + 1)
                    + ["#000000", "#ffffff"]
                    + ["images/placeholder.png", ""]
                )

            with gr.Blocks(title="QRGen") as demo:
                # language selection (default from env or 'en')
                lang = os.environ.get("QRGEN_LANG", "en")
                from .i18n import available_languages, LANG_NAMES

                # Top-level title and instruction as components so they can be updated
                title_md = gr.Markdown(f"# {t('title', lang)}")
                instr_md = gr.Markdown(t("choose_format_instruction", lang))
                # (language selector moved into Settings tab so it's grouped with other controls)
                with gr.Tabs():
                    # vCard Tab (reuses existing template-driven inputs)
                    with gr.TabItem(t("tab_vcard", lang)):
                        with gr.Row():
                            with gr.Column(scale=1):
                                vcard_inputs = []
                                for field in self.user_fields:
                                    vcard_inputs.append(
                                        gr.Textbox(
                                            label=field,
                                            placeholder=DEFAULT_VCARD_FIELDS[field],
                                            info=self.field_descriptions.get(field, ""),
                                        )
                                    )
                                vcard_logo = gr.File(
                                    label=t("logo_optional", lang), visible=False
                                )
                                vcard_fg = gr.ColorPicker(
                                    label=t("qr_color", lang),
                                    value="#000000",
                                    visible=False,
                                )
                                vcard_bg = gr.ColorPicker(
                                    label=t("bg_color", lang),
                                    value="#ffffff",
                                    visible=False,
                                )
                            with gr.Column(scale=1):
                                # Settings controls will be read from Settings tab via shared components
                                vcard_generate = gr.Button(
                                    t("generate_vcard", lang), variant="primary"
                                )
                                vcard_preview_img = gr.Image(
                                    label=t("qr_preview", lang),
                                    value="images/placeholder.png",
                                )
                                vcard_payload_preview = gr.Textbox(
                                    label=t("payload_preview", lang), lines=6
                                )

                    with gr.TabItem(t("tab_url", lang)):
                        with gr.Row():
                            with gr.Column(scale=1):
                                url_input = gr.Textbox(
                                    label=t("label_url", lang),
                                    placeholder=t("placeholder_url", lang),
                                )
                                url_logo = gr.File(
                                    label=t("logo_optional", lang), visible=False
                                )
                                url_fg = gr.ColorPicker(
                                    label=t("qr_color", lang),
                                    value="#000000",
                                    visible=False,
                                )
                                url_bg = gr.ColorPicker(
                                    label=t("bg_color", lang),
                                    value="#ffffff",
                                    visible=False,
                                )
                            with gr.Column(scale=1):
                                url_generate = gr.Button(t("generate_url", lang), variant="primary")
                                url_preview_img = gr.Image(
                                    label=t("qr_preview", lang),
                                    value="images/placeholder.png",
                                )
                                url_payload_preview = gr.Textbox(
                                    label=t("payload_preview", lang), lines=6
                                )

                    with gr.TabItem(t("tab_text", lang)):
                        with gr.Row():
                            with gr.Column(scale=1):
                                text_input = gr.Textbox(
                                    label=t("label_text", lang), lines=6
                                )
                                text_logo = gr.File(
                                    label=t("logo_optional", lang), visible=False
                                )
                                text_fg = gr.ColorPicker(
                                    label=t("qr_color", lang),
                                    value="#000000",
                                    visible=False,
                                )
                                text_bg = gr.ColorPicker(
                                    label=t("bg_color", lang),
                                    value="#ffffff",
                                    visible=False,
                                )
                            with gr.Column(scale=1):
                                text_generate = gr.Button(t("generate_text", lang), variant="primary")
                                text_preview_img = gr.Image(
                                    label=t("qr_preview", lang),
                                    value="images/placeholder.png",
                                )
                                text_payload_preview = gr.Textbox(
                                    label=t("payload_preview", lang), lines=6
                                )

                    with gr.TabItem(t("tab_email", lang)):
                        with gr.Row():
                            with gr.Column(scale=1):
                                mail_to = gr.Textbox(label=t("label_to", lang))
                                mail_subject = gr.Textbox(
                                    label=t("label_subject", lang)
                                )
                                mail_body = gr.Textbox(
                                    label=t("label_body", lang), lines=4
                                )
                                mail_logo = gr.File(
                                    label=t("logo_optional", lang), visible=False
                                )
                                mail_fg = gr.ColorPicker(
                                    label=t("qr_color", lang),
                                    value="#000000",
                                    visible=False,
                                )
                                mail_bg = gr.ColorPicker(
                                    label=t("bg_color", lang),
                                    value="#ffffff",
                                    visible=False,
                                )
                            with gr.Column(scale=1):
                                mail_generate = gr.Button(t("generate_mailto", lang), variant="primary")
                                mail_preview_img = gr.Image(
                                    label=t("qr_preview", lang),
                                    value="images/placeholder.png",
                                )
                                mail_payload_preview = gr.Textbox(
                                    label=t("payload_preview", lang), lines=6
                                )

                    with gr.TabItem(t("tab_phone", lang)):
                        with gr.Row():
                            with gr.Column(scale=1):
                                phone_input = gr.Textbox(
                                    label=t("label_phone_number", lang)
                                )
                                phone_logo = gr.File(
                                    label=t("logo_optional", lang), visible=False
                                )
                                phone_fg = gr.ColorPicker(
                                    label=t("qr_color", lang),
                                    value="#000000",
                                    visible=False,
                                )
                                phone_bg = gr.ColorPicker(
                                    label=t("bg_color", lang),
                                    value="#ffffff",
                                    visible=False,
                                )
                            with gr.Column(scale=1):
                                phone_generate = gr.Button(t("generate_phone", lang), variant="primary")
                                phone_preview_img = gr.Image(
                                    label=t("qr_preview", lang),
                                    value="images/placeholder.png",
                                )
                                phone_payload_preview = gr.Textbox(
                                    label=t("payload_preview", lang), lines=6
                                )

                    with gr.TabItem(t("tab_sms", lang)):
                        with gr.Row():
                            with gr.Column(scale=1):
                                sms_phone = gr.Textbox(
                                    label=t("label_phone_number", lang)
                                )
                                sms_message = gr.Textbox(
                                    label=t("label_message", lang), lines=4
                                )
                                sms_logo = gr.File(
                                    label=t("logo_optional", lang), visible=False
                                )
                                sms_fg = gr.ColorPicker(
                                    label=t("qr_color", lang),
                                    value="#000000",
                                    visible=False,
                                )
                                sms_bg = gr.ColorPicker(
                                    label=t("bg_color", lang),
                                    value="#ffffff",
                                    visible=False,
                                )
                            with gr.Column(scale=1):
                                sms_generate = gr.Button(t("generate_sms", lang), variant="primary")
                                sms_preview_img = gr.Image(
                                    label=t("qr_preview", lang),
                                    value="images/placeholder.png",
                                )
                                sms_payload_preview = gr.Textbox(
                                    label=t("payload_preview", lang), lines=6
                                )

                    with gr.TabItem(t("tab_wifi", lang)):
                        with gr.Row():
                            with gr.Column(scale=1):
                                wifi_ssid = gr.Textbox(label=t("label_ssid", lang))
                                wifi_auth = gr.Dropdown(
                                    choices=["WPA", "WEP", "nopass"],
                                    value="WPA",
                                    label=t("label_auth_type", lang),
                                )
                                wifi_password = gr.Textbox(
                                    label=t("label_password", lang)
                                )
                                wifi_hidden = gr.Checkbox(
                                    label=t("label_hidden_network", lang)
                                )
                                wifi_logo = gr.File(
                                    label=t("logo_optional", lang), visible=False
                                )
                                wifi_fg = gr.ColorPicker(
                                    label=t("qr_color", lang),
                                    value="#000000",
                                    visible=False,
                                )
                                wifi_bg = gr.ColorPicker(
                                    label=t("bg_color", lang),
                                    value="#ffffff",
                                    visible=False,
                                )
                            with gr.Column(scale=1):
                                wifi_generate = gr.Button(t("generate_wifi", lang), variant="primary")
                                wifi_preview_img = gr.Image(
                                    label=t("qr_preview", lang),
                                    value="images/placeholder.png",
                                )
                                wifi_payload_preview = gr.Textbox(
                                    label=t("payload_preview", lang), lines=6
                                )

                    with gr.TabItem(t("tab_event", lang)):
                        with gr.Row():
                            with gr.Column(scale=1):
                                evt_summary = gr.Textbox(label=t("label_summary", lang))
                                evt_start = gr.Textbox(label=t("label_start", lang))
                                evt_end = gr.Textbox(
                                    label=t("label_end_optional", lang)
                                )
                                evt_location = gr.Textbox(
                                    label=t("label_location", lang)
                                )
                                evt_description = gr.Textbox(
                                    label=t("label_description", lang), lines=4
                                )
                                evt_logo = gr.File(
                                    label=t("logo_optional", lang), visible=False
                                )
                                evt_fg = gr.ColorPicker(
                                    label=t("qr_color", lang),
                                    value="#000000",
                                    visible=False,
                                )
                                evt_bg = gr.ColorPicker(
                                    label=t("bg_color", lang),
                                    value="#ffffff",
                                    visible=False,
                                )
                            with gr.Column(scale=1):
                                evt_generate = gr.Button(t("generate_event", lang), variant="primary")
                                evt_preview_img = gr.Image(
                                    label=t("qr_preview", lang),
                                    value="images/placeholder.png",
                                )
                                evt_payload_preview = gr.Textbox(
                                    label=t("payload_preview", lang), lines=6
                                )

                    with gr.TabItem(t("tab_geo", lang)):
                        with gr.Row():
                            with gr.Column(scale=1):
                                geo_lat = gr.Textbox(label=t("label_latitude", lang))
                                geo_lon = gr.Textbox(label=t("label_longitude", lang))
                                geo_label = gr.Textbox(
                                    label=t("label_label_optional", lang)
                                )
                                geo_logo = gr.File(
                                    label=t("logo_optional", lang), visible=False
                                )
                                geo_fg = gr.ColorPicker(
                                    label=t("qr_color", lang),
                                    value="#000000",
                                    visible=False,
                                )
                                geo_bg = gr.ColorPicker(
                                    label=t("bg_color", lang),
                                    value="#ffffff",
                                    visible=False,
                                )
                            with gr.Column(scale=1):
                                geo_generate = gr.Button(t("generate_geo", lang), variant="primary")
                                geo_preview_img = gr.Image(
                                    label=t("qr_preview", lang),
                                    value="images/placeholder.png",
                                )
                                geo_payload_preview = gr.Textbox(
                                    label=t("payload_preview", lang), lines=6
                                )

                    with gr.TabItem(t("tab_applink", lang)):
                        with gr.Row():
                            with gr.Column(scale=1):
                                app_url = gr.Textbox(
                                    label=t("label_app_url_fallback", lang)
                                )
                                app_logo = gr.File(
                                    label=t("logo_optional", lang), visible=False
                                )
                                app_fg = gr.ColorPicker(
                                    label=t("qr_color", lang),
                                    value="#000000",
                                    visible=False,
                                )
                                app_bg = gr.ColorPicker(
                                    label=t("bg_color", lang),
                                    value="#ffffff",
                                    visible=False,
                                )
                            with gr.Column(scale=1):
                                app_generate = gr.Button(t("generate_applink", lang), variant="primary")
                                app_preview_img = gr.Image(
                                    label=t("qr_preview", lang),
                                    value="images/placeholder.png",
                                )
                                app_payload_preview = gr.Textbox(
                                    label=t("payload_preview", lang), lines=6
                                )

                    with gr.TabItem(t("tab_payment", lang)):
                        with gr.Row():
                            with gr.Column(scale=1):
                                pay_address = gr.Textbox(label=t("label_address", lang))
                                pay_amount = gr.Textbox(
                                    label=t("label_amount_optional", lang)
                                )
                                pay_label = gr.Textbox(
                                    label=t("label_label_optional", lang)
                                )
                                pay_logo = gr.File(
                                    label=t("logo_optional", lang), visible=False
                                )
                                pay_fg = gr.ColorPicker(
                                    label=t("qr_color", lang),
                                    value="#000000",
                                    visible=False,
                                )
                                pay_bg = gr.ColorPicker(
                                    label=t("bg_color", lang),
                                    value="#ffffff",
                                    visible=False,
                                )
                            with gr.Column(scale=1):
                                pay_generate = gr.Button(t("generate_payment", lang), variant="primary")
                                pay_preview_img = gr.Image(
                                    label=t("qr_preview", lang),
                                    value="images/placeholder.png",
                                )
                                pay_payload_preview = gr.Textbox(
                                    label=t("payload_preview", lang), lines=6
                                )

                    with gr.TabItem(t("tab_mecard", lang)):
                        with gr.Row():
                            with gr.Column(scale=1):
                                me_name = gr.Textbox(label=t("label_name", lang))
                                me_tel = gr.Textbox(label=t("label_phone", lang))
                                me_email = gr.Textbox(label=t("label_email", lang))
                                me_org = gr.Textbox(label=t("label_organization", lang))
                                me_note = gr.Textbox(label=t("label_note", lang))
                                me_logo = gr.File(
                                    label=t("logo_optional", lang), visible=False
                                )
                                me_fg = gr.ColorPicker(
                                    label=t("qr_color", lang),
                                    value="#000000",
                                    visible=False,
                                )
                                me_bg = gr.ColorPicker(
                                    label=t("bg_color", lang),
                                    value="#ffffff",
                                    visible=False,
                                )
                            with gr.Column(scale=1):
                                me_generate = gr.Button(t("generate_mecard", lang), variant="primary")
                                me_preview_img = gr.Image(
                                    label=t("qr_preview", lang),
                                    value="images/placeholder.png",
                                )
                                me_payload_preview = gr.Textbox(
                                    label=t("payload_preview", lang), lines=6
                                )

                    with gr.TabItem(t("tab_settings", lang)):
                        with gr.Row():
                            save_settings_btn = gr.Button(
                                t("save_settings", lang), variant="primary"
                            )
                            reset_settings_btn = gr.Button(
                                t("reset_settings", lang), variant="secondary"
                            )
                        settings_status = gr.Markdown("")
                        with gr.Row():
                            with gr.Column(scale=1):
                                settings_preview_img = gr.Image(
                                    label="Settings Test QR",
                                    value="images/placeholder.png",
                                )

                                from .i18n import available_languages, LANG_NAMES

                                lang_choices = [
                                    f"{LANG_NAMES.get(c, c)} ({c})"
                                    for c in available_languages()
                                ]
                                lang_map = {
                                    f"{LANG_NAMES.get(c, c)} ({c})": c
                                    for c in available_languages()
                                }
                                lang_select = gr.Dropdown(
                                    choices=lang_choices,
                                    value=f"{LANG_NAMES.get(lang, lang)} ({lang})",
                                    label=t("language", lang),
                                )

                                qr_customization_md = gr.Markdown(
                                    "## " + t("Customization", lang)
                                )
                                size_slider = gr.Slider(
                                    minimum=100,
                                    maximum=1200,
                                    value=240,
                                    step=10,
                                    label=t("qr_size", lang),
                                )
                                ec_dropdown = gr.Dropdown(
                                    choices=["L", "M", "Q", "H"],
                                    value="H",
                                    label=t("error_correction", lang),
                                )
                                max_payload = gr.Number(
                                    value=1000, label=t("max_payload", lang)
                                )

                                qr_border_md = gr.Markdown("### " + t("Border", lang))
                                border_slider = gr.Slider(
                                    minimum=0,
                                    maximum=200,
                                    value=0,
                                    step=1,
                                    label=t("border", lang),
                                )
                                corner_radius = gr.Slider(
                                    minimum=0,
                                    maximum=200,
                                    value=0,
                                    step=1,
                                    label=t("corner_radius", lang),
                                )
                                qr_corner_radius = gr.Slider(
                                    minimum=0,
                                    maximum=200,
                                    value=0,
                                    step=1,
                                    label="QR " + t("corner_radius", lang),
                                )
                                border_color_picker = gr.ColorPicker(
                                    label=t("border_color", lang), value="#000000"
                                )

                                qr_colours_md = gr.Markdown("### " + t("Color", lang))
                                transparent_bg = gr.Checkbox(
                                    label=t("transparent_bg", lang), value=False
                                )
                                palette_dropdown = gr.Dropdown(
                                    label=t("palette", lang),
                                    choices=[
                                        "Classic",
                                        "Brand Blue",
                                        "Warm Sunset",
                                        "Forest",
                                        "Violet",
                                        "Slate",
                                        "Custom",
                                    ],
                                    value="Classic",
                                )
                                with gr.Row():
                                    custom_fg = gr.ColorPicker(
                                        label=t("foreground_color", lang),
                                        value="#000000",
                                        visible=False,
                                    )
                                    custom_bg = gr.ColorPicker(
                                        label=t("bg_color", lang),
                                        value="#ffffff",
                                        visible=False,
                                    )

                                qr_gradient_md = gr.Markdown(
                                    "### " + t("Gradient", lang)
                                )
                                gradient_toggle = gr.Checkbox(
                                    label=t("enable_gradient", lang), value=False
                                )
                                gradient_palette = gr.Dropdown(
                                    label=t("gradient_palette", lang),
                                    choices=[
                                        "Classic",
                                        "Brand Blue",
                                        "Warm Sunset",
                                        "Forest",
                                        "Violet",
                                        "Slate",
                                        "Custom",
                                    ],
                                    value="Classic",
                                )
                                with gr.Row():
                                    gradient_from = gr.ColorPicker(
                                        label=t("gradient_from", lang),
                                        value="#000000",
                                        visible=False,
                                    )
                                    gradient_to = gr.ColorPicker(
                                        label=t("gradient_to", lang),
                                        value="#ffffff",
                                        visible=False,
                                    )
                                gradient_target = gr.Dropdown(
                                    label=t("gradient_target", lang),
                                    choices=["Background", "Foreground"],
                                    value="Background",
                                )
                                gradient_angle = gr.Slider(
                                    label=t("gradient_angle", lang),
                                    minimum=0,
                                    maximum=360,
                                    value=90,
                                    step=5,
                                )

                                qr_appearance_md = gr.Markdown(
                                    "### " + t("Appearance", lang)
                                )
                                with gr.Row():
                                    shape_dropdown = gr.Dropdown(
                                        label=t("module_shape", lang),
                                        choices=["square", "rounded", "dot", "circle"],
                                        value="square",
                                    )
                                    pattern_dropdown = gr.Dropdown(
                                        label=t("pattern", lang),
                                        choices=[
                                            "standard",
                                            "eyes-rounded",
                                            "eyes-square",
                                            "scatter",
                                        ],
                                        value="standard",
                                    )
                                pattern_strength = gr.Slider(
                                    label=t("pattern_strength", lang),
                                    minimum=0,
                                    maximum=100,
                                    value=50,
                                    step=5,
                                )

                                qr_files_md = gr.Markdown("## " + t("Files", lang))

                                upload_batch_csv = gr.File(
                                    label=t("upload_csv", lang),
                                    file_types=[".csv"],
                                    visible=True,
                                )
                                with gr.Row():
                                    download_batch_btn = gr.Button(
                                        t("download_batch", lang), variant="secondary"
                                    )
                                    download_template_btn = gr.Button(
                                        t("download_template", lang),
                                        variant="secondary",
                                    )

                                # Download outputs
                                download_batch_file = gr.File(
                                    label="Batch ZIP", visible=False
                                )

                            with gr.Column(scale=1):
                                logo_md = gr.Markdown("### " + t("logo_section", lang))
                                shared_logo = gr.File(label=t("logo_optional", lang))
                                shared_logo_enable = gr.Checkbox(label=t('enable_logo', lang), value=False)
                                logo_preview = gr.Image(
                                    label=t("logo_preview", lang),
                                    value="images/placeholder.png",
                                )
                                logo_scale = gr.Slider(
                                    label=t("logo_scale", lang),
                                    minimum=0.01,
                                    maximum=0.5,
                                    value=0.2,
                                    step=0.01,
                                )
                                logo_opacity = gr.Slider(
                                    label=t("logo_opacity", lang),
                                    minimum=0.0,
                                    maximum=1.0,
                                    value=1.0,
                                    step=0.05,
                                )
                                logo_clip = gr.Dropdown(
                                    label=t("logo_clip", lang),
                                    choices=["none", "circle", "square"],
                                    value="none",
                                )

                                qr_text_md = gr.Markdown("### " + t("Text", lang))
                                header_text = gr.Textbox(
                                    label=t("header_text", lang),
                                    value="",
                                    placeholder="",
                                )
                                footer_text = gr.Textbox(
                                    label=t("footer_text", lang),
                                    value="",
                                    placeholder="",
                                )

                                qr_header_md = gr.Markdown("### " + t("Header", lang))
                                header_font_select = gr.Dropdown(
                                    choices=[
                                        "Default",
                                        "DejaVuSans",
                                        "DejaVuSans-Bold",
                                    ],
                                    value="Default",
                                    label=t("font", lang),
                                )
                                header_font_slider = gr.Slider(
                                    minimum=8,
                                    maximum=72,
                                    value=16,
                                    step=1,
                                    label=t("header_font_size", lang),
                                )
                                header_font_file = gr.File(
                                    label=t("font", lang) + " (TTF)", visible=True
                                )
                                header_bold = gr.Checkbox(
                                    label=t("bold", lang), value=False
                                )
                                header_align = gr.Dropdown(
                                    choices=["left", "center", "right"],
                                    value="center",
                                    label=t("align", lang),
                                )

                                qr_footer_md = gr.Markdown("### " + t("Footer", lang))
                                footer_font_select = gr.Dropdown(
                                    choices=[
                                        "Default",
                                        "DejaVuSans",
                                        "DejaVuSans-Bold",
                                    ],
                                    value="Default",
                                    label=t("font", lang),
                                )
                                footer_font_slider = gr.Slider(
                                    minimum=8,
                                    maximum=72,
                                    value=14,
                                    step=1,
                                    label=t("footer_font_size", lang),
                                )
                                footer_font_file = gr.File(
                                    label=t("font", lang) + " (TTF)", visible=True
                                )
                                footer_bold = gr.Checkbox(
                                    label=t("bold", lang), value=False
                                )
                                footer_align = gr.Dropdown(
                                    choices=["left", "center", "right"],
                                    value="center",
                                    label=t("align", lang),
                                )

                # Handler to update visible labels when language selection changes
                def _update_ui(selected_display):
                    sel = lang_map.get(selected_display, "en")
                    from .i18n import localized_language_choices

                    choices, display_to_code_new, code_to_display_new = (
                        localized_language_choices(sel)
                    )
                    # Return update objects in the same order as outputs below
                    return (
                        gr.update(value=f"# {t('title', sel)}"),
                        gr.update(value=t("choose_format_instruction", sel)),
                        gr.update(value=t("generate_vcard", sel)),
                        gr.update(value=t("generate_url", sel)),
                        gr.update(value=t("generate_text", sel)),
                        gr.update(value=t("generate_mailto", sel)),
                        gr.update(value=t("generate_phone", sel)),
                        gr.update(value=t("generate_sms", sel)),
                        gr.update(value=t("generate_wifi", sel)),
                        gr.update(value=t("generate_event", sel)),
                        gr.update(value=t("generate_geo", sel)),
                        gr.update(value=t("generate_applink", sel)),
                        gr.update(value=t("generate_payment", sel)),
                        gr.update(value=t("generate_mecard", sel)),
                        gr.update(label=t("label_url", sel)),
                        gr.update(label=t("label_text", sel)),
                        gr.update(label=t("label_to", sel)),
                        gr.update(label=t("label_subject", sel)),
                        gr.update(label=t("label_body", sel)),
                        gr.update(label=t("label_phone_number", sel)),
                        gr.update(label=t("label_phone_number", sel)),
                        gr.update(label=t("label_message", sel)),
                        gr.update(label=t("label_ssid", sel)),
                        gr.update(label=t("label_auth_type", sel)),
                        gr.update(label=t("label_password", sel)),
                        gr.update(label=t("label_hidden_network", sel)),
                        gr.update(label=t("label_summary", sel)),
                        gr.update(label=t("label_start", sel)),
                        gr.update(label=t("label_end_optional", sel)),
                        gr.update(label=t("label_location", sel)),
                        gr.update(label=t("label_description", sel)),
                        gr.update(label=t("label_latitude", sel)),
                        gr.update(label=t("label_longitude", sel)),
                        gr.update(label=t("label_label_optional", sel)),
                        gr.update(label=t("label_app_url_fallback", sel)),
                        gr.update(label=t("label_address", sel)),
                        gr.update(label=t("label_amount_optional", sel)),
                        gr.update(label=t("label_label_optional", sel)),
                        gr.update(label=t("label_name", sel)),
                        gr.update(label=t("label_phone", sel)),
                        gr.update(label=t("label_email", sel)),
                        gr.update(label=t("label_organization", sel)),
                        gr.update(label=t("label_note", sel)),
                        gr.update(value="## " + t("Customization", sel)),  # customization header
                        gr.update(label=t("qr_size", sel)),
                        gr.update(label=t("error_correction", sel)),
                        gr.update(label=t("max_payload", sel)),
                        gr.update(value="### " + t("Border", sel)),  # border header
                        gr.update(label=t("border", sel)),
                        gr.update(label=t("corner_radius", sel)),
                        gr.update(label="QR " + t("corner_radius", sel)),
                        gr.update(label=t("border_color", sel)),
                        gr.update(value="### " + t("Color", sel)),  # colours header
                        gr.update(label=t("transparent_bg", sel)),
                        gr.update(label=t("palette", sel)),
                        gr.update(label=t("foreground_color", sel)),
                        gr.update(label=t("bg_color", sel)),
                        gr.update(value="### " + t("Gradient", sel)),  # gradient header
                        gr.update(label=t("enable_gradient", sel)),
                        gr.update(label=t("gradient_palette", sel)),
                        gr.update(label=t("gradient_from", sel)),
                        gr.update(label=t("gradient_to", sel)),
                        gr.update(label=t("gradient_target", sel)),
                        gr.update(label=t("gradient_angle", sel)),
                        gr.update(value="### " + t("Appearance", sel)),  # appearance header
                        gr.update(label=t("module_shape", sel)),
                        gr.update(label=t("pattern", sel)),
                        gr.update(label=t("pattern_strength", sel)),
                        gr.update(value="## " + t("Files", sel)),  # files header
                        gr.update(label=t("upload_csv", sel)),
                        gr.update(value=t("download_batch", sel)),
                        gr.update(value=t("download_template", sel)),
                        gr.update(value="### " + t("logo_section", sel)),  # logo header
                        gr.update(label=t("logo_optional", sel)),
                        gr.update(label=t("enable_logo", sel)),
                        gr.update(label=t("logo_preview", sel)),
                        gr.update(label=t("logo_scale", sel)),
                        gr.update(label=t("logo_opacity", sel)),
                        gr.update(
                            label=t("logo_clip", sel),
                            choices=["none", "circle", "square"],
                            value="none",
                        ),
                        gr.update(value="### " + t("Text", sel)),  # text header
                        gr.update(label=t("header_text", sel)),
                        gr.update(label=t("footer_text", sel)),
                        gr.update(value="### " + t("Header", sel)),  # header header
                        gr.update(label=t("font", sel)),
                        gr.update(label=t("header_font_size", sel)),
                        gr.update(label=t("font", sel) + " (TTF)"),
                        gr.update(label=t("bold", sel)),
                        gr.update(label=t("align", sel)),
                        gr.update(value="### " + t("Footer", sel)),  # footer header
                        gr.update(label=t("font", sel)),
                        gr.update(label=t("footer_font_size", sel)),
                        gr.update(label=t("font", sel) + " (TTF)"),
                        gr.update(label=t("bold", sel)),
                        gr.update(label=t("align", sel)),
                        gr.update(
                            choices=choices,
                            value=code_to_display_new.get(sel, choices[0]),
                            label=t("language", sel),
                        ),
                        gr.update(value=""),  # settings_status
                        gr.update(value=t("save_settings", sel)),
                        gr.update(value=t("reset_settings", sel)),
                        gr.update(choices=["square", "rounded", "dot", "circle"]),  # 98: shape_dropdown
                        gr.update(choices=["Custom", "Nord", "Retro", "Sunset", "Ocean"]), # 99: gradient_palette
                    )

                # Save settings test: generate a small test QR to preview current settings
                def _save_settings_and_preview(*shared_args):
                    try:
                        res = gen_generic("QRGen Test Image", *shared_args)
                        if isinstance(res, tuple) and len(res) >= 2:
                            return res[0]
                        return "images/placeholder.png"
                    except Exception:
                        logging.exception("Failed to generate settings preview")
                        return "images/placeholder.png"

                # Callbacks: update palette color pickers and visibility when palette changes
                def _update_palette(pal):
                    try:
                        from .styles import resolve_palette

                        if pal and pal != "Custom":
                            fg, bg = resolve_palette(pal, None, None)
                            return gr.update(value=fg, visible=False), gr.update(
                                value=bg, visible=False
                            )
                    except Exception:
                        pass
                    # If Custom, make color pickers visible (user can pick)
                    if pal == "Custom":
                        return gr.update(visible=True), gr.update(visible=True)
                    return gr.update(visible=False), gr.update(visible=False)

                def _update_gradient_palette(pal):
                    try:
                        from .styles import resolve_palette

                        if pal and pal != "Custom":
                            fg, bg = resolve_palette(pal, None, None)
                            return gr.update(value=fg, visible=False), gr.update(
                                value=bg, visible=False
                            )
                    except Exception:
                        pass
                    if pal == "Custom":
                        return gr.update(visible=True), gr.update(visible=True)
                    return gr.update(visible=False), gr.update(visible=False)

                def _save_logo_and_preview(f):
                    try:
                        if not f:
                            return "images/placeholder.png"
                        # Ensure output dir exists
                        out_dir = os.path.join(os.getcwd(), "output")
                        os.makedirs(out_dir, exist_ok=True)
                        dst = os.path.join(
                            out_dir, "tmp_logo" + os.path.splitext(f.name)[1]
                        )
                        # Copy uploaded file to persistent location
                        shutil.copyfile(f.name, dst)
                        return dst
                    except Exception:
                        return "images/placeholder.png"

                # Save settings: persist simple settings to output/settings.json and generate preview
                def _save_settings(*shared_args):
                    try:
                        # Persist to JSON (shallow mapping)
                        import json

                        out_dir = os.path.join(os.getcwd(), "output")
                        os.makedirs(out_dir, exist_ok=True)
                        keys = [
                            "shared_logo",
                            "shared_logo_enable",
                            "palette",
                            "transparent_bg",
                            "use_gradient",
                            "gradient_target",
                            "gradient_from",
                            "gradient_to",
                            "gradient_angle",
                            "custom_fg",
                            "custom_bg",
                            "shape",
                            "pattern",
                            "pattern_strength",
                            "logo_scale",
                            "logo_opacity",
                            "logo_clip",
                            "border",
                            "border_color",
                            "corner_radius",
                            "qr_corner_radius",
                            "header_text",
                            "footer_text",
                            "header_font_size",
                            "footer_font_size",
                            "header_font_select",
                            "header_font_file",
                            "header_bold",
                            "header_align",
                            "footer_font_select",
                            "footer_font_file",
                            "footer_bold",
                            "footer_align",
                            "size",
                            "ec",
                            "gradient_palette",
                        ]
                        # Map positional shared_args into dict
                        shared_vals = list(shared_args[: len(keys)])
                        while len(shared_vals) < len(keys):
                            shared_vals.append(None)
                        data = dict(zip(keys, shared_vals))
                        with open(
                            os.path.join(out_dir, "settings.json"),
                            "w",
                            encoding="utf-8",
                        ) as fh:
                            json.dump(data, fh, indent=2)

                        # Generate preview image using current settings
                        res = gen_generic("QRGen Settings Preview", *shared_args)
                        img = (
                            res[0]
                            if isinstance(res, tuple) and len(res) >= 1
                            else "images/placeholder.png"
                        )
                        return img, t("settings_saved", lang)
                    except Exception:
                        logging.exception("Failed to save settings")
                        return "images/placeholder.png", t("settings_saved", lang)

                def _download_batch(csv_file, *shared_args):
                    """Create a ZIP containing sample QR PNGs for each row in csv_file (or a sample if none) and return path to zip."""
                    try:
                        out_dir = os.path.join(os.getcwd(), "output")
                        os.makedirs(out_dir, exist_ok=True)
                        zip_path = os.path.join(out_dir, "qr_batch.zip")
                        import zipfile
                        import csv
                        from .payloads import (
                            build_url,
                            build_text,
                            build_mailto,
                            build_tel,
                            build_sms,
                            build_wifi,
                            build_geo,
                            build_event,
                            build_applink,
                            build_payment,
                            build_mecard,
                        )

                        # Create temp files inside out_dir/tmp_batch
                        tmp_dir = os.path.join(out_dir, "tmp_batch")
                        if os.path.isdir(tmp_dir):
                            import shutil

                            shutil.rmtree(tmp_dir)
                        os.makedirs(tmp_dir, exist_ok=True)

                        rows = []
                        if csv_file and getattr(csv_file, "name", None):
                            with open(csv_file.name, "r", encoding="utf-8") as fh:
                                rdr = csv.reader(fh)
                                header = next(rdr, None)
                                # Simple check: if first column of first row is 'Format', it's our template
                                if header:
                                    if header[0].lower() == "format":
                                        pass  # skip header
                                    else:
                                        rows.append(header)
                                for r in rdr:
                                    if r:
                                        rows.append(r)
                        if not rows:
                            rows = [["text", "Sample QR 1"], ["text", "Sample QR 2"]]

                        for i, r in enumerate(rows, start=1):
                            if len(r) >= 2:
                                fmt, data = r[0], r[1]
                                parts = [p.strip() for p in data.split("|")]
                                fmt = fmt.strip().lower()

                                try:
                                    if fmt == "url":
                                        payload = build_url(parts[0])
                                    elif fmt == "text":
                                        payload = build_text(parts[0])
                                    elif fmt == "wifi":
                                        payload = build_wifi(
                                            parts[0],
                                            parts[1] if len(parts) > 1 else "WPA",
                                            parts[2] if len(parts) > 2 else None,
                                            (parts[3].lower() == "true")
                                            if len(parts) > 3
                                            else False,
                                        )
                                    elif fmt == "sms":
                                        payload = build_sms(
                                            parts[0], parts[1] if len(parts) > 1 else None
                                        )
                                    elif fmt == "tel":
                                        payload = build_tel(parts[0])
                                    elif fmt == "mailto":
                                        payload = build_mailto(
                                            parts[0],
                                            parts[1] if len(parts) > 1 else None,
                                            parts[2] if len(parts) > 2 else None,
                                        )
                                    elif fmt == "geo":
                                        payload = build_geo(
                                            parts[0],
                                            parts[1],
                                            parts[2] if len(parts) > 2 else None,
                                        )
                                    elif fmt == "event":
                                        payload = build_event(
                                            parts[0],
                                            parts[1],
                                            parts[2] if len(parts) > 2 else None,
                                            parts[3] if len(parts) > 3 else None,
                                            parts[4] if len(parts) > 4 else None,
                                        )
                                    elif fmt == "payment":
                                        payload = build_payment(
                                            parts[0],
                                            parts[1] if len(parts) > 1 else None,
                                            parts[2] if len(parts) > 2 else None,
                                        )
                                    elif fmt == "mecard":
                                        payload = build_mecard(
                                            parts[0],
                                            parts[1] if len(parts) > 1 else None,
                                            parts[2] if len(parts) > 2 else None,
                                            parts[3] if len(parts) > 3 else None,
                                            parts[4] if len(parts) > 4 else None,
                                        )
                                    elif fmt == "vcard":
                                        vcard_dict = {}
                                        for p in parts:
                                            if ":" in p:
                                                k, v = p.split(":", 1)
                                                vcard_dict[k.strip()] = v.strip()
                                        from .payloads import build_vcard

                                        payload = build_vcard(vcard_dict)
                                    else:
                                        payload = data
                                except Exception:
                                    payload = data
                            else:
                                payload = r[0]

                            # Generate a PNG for each
                            fname = os.path.join(tmp_dir, f"qr_{i}.png")
                            # Reuse generate_qr to write file to destination
                            try:
                                generate_qr(
                                    payload,
                                    dest=fname,
                                    size=512,
                                    fill_color="black",
                                    back_color="white",
                                )
                            except Exception:
                                # Fallback: write placeholder file
                                from PIL import Image

                                Image.new(
                                    "RGBA", (512, 512), (255, 255, 255, 255)
                                ).save(fname)

                        # Zip them
                        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                            for root, dirs, files in os.walk(tmp_dir):
                                for f in files:
                                    zf.write(os.path.join(root, f), arcname=f)
                        return zip_path
                    except Exception:
                        logging.exception("Failed to build batch zip")
                        return None

                def _download_template():
                    """Create a sample CSV template for batch generation and return its path."""
                    try:
                        out_dir = os.path.join(os.getcwd(), "output")
                        os.makedirs(out_dir, exist_ok=True)
                        template_path = os.path.join(out_dir, "batch_template.csv")
                        import csv

                        with open(template_path, "w", encoding="utf-8", newline="") as fh:
                            writer = csv.writer(fh)
                            writer.writerow(["Format", "Data"])
                            writer.writerow(["url", "https://example.com"])
                            writer.writerow(["text", "Hello World"])
                            writer.writerow(["wifi", "HomeNetwork|WPA|SecretPassword|false"])
                            writer.writerow(["sms", "12345678|Hello from QR"])
                            writer.writerow(["tel", "12345678"])
                            writer.writerow(["mailto", "test@example.com|Subject|Body"])
                            writer.writerow(["geo", "-22.5|17.1|Windhoek"])
                            writer.writerow(
                                [
                                    "event",
                                    "Meeting|20260101T100000|20260101T110000|Office|Monthly Sync",
                                ]
                            )
                            writer.writerow(
                                [
                                    "payment",
                                    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa|0.01|Donation",
                                ]
                            )
                            writer.writerow(
                                ["mecard", "John Doe|12345678|john@example.com|ACME Corp|Friend"]
                            )
                            writer.writerow(
                                ["vcard", "FN:John Doe|ORG:ACME Corp|TEL;TYPE=CELL:12345678"]
                            )
                        return template_path
                    except Exception:
                        logging.exception("Failed to build CSV template")
                        return None

                def _reset_to_defaults():
                    # Return a sequence of gr.update(...) results matching the settings controls order used elsewhere
                    try:
                        return (
                            gr.update(value=240),  # size_slider
                            gr.update(value="H"),  # ec_dropdown
                            gr.update(value=1000),  # max_payload
                            gr.update(value=False),  # transparent_bg
                            gr.update(value="Classic"),  # palette_dropdown
                            gr.update(value=False),  # gradient_toggle
                            gr.update(value="#000000", visible=False),  # gradient_from
                            gr.update(value="#ffffff", visible=False),  # gradient_to
                            gr.update(value=90),  # gradient_angle
                            gr.update(value="Background"),  # gradient_target
                            gr.update(value="#000000", visible=False),  # custom_fg
                            gr.update(value="#ffffff", visible=False),  # custom_bg
                            gr.update(value="square"),  # shape_dropdown
                            gr.update(value="standard"),  # pattern_dropdown
                            gr.update(value=50),  # pattern_strength
                            gr.update(value=False),  # shared_logo_enable
                            gr.update(value="images/placeholder.png"),  # logo_preview
                            gr.update(value=0.2),  # logo_scale
                            gr.update(value=1.0),  # logo_opacity
                            gr.update(value="none"),  # logo_clip
                            gr.update(value=0),  # border_slider
                            gr.update(value="#000000"),  # border_color_picker
                            gr.update(value=0),  # corner_radius
                            gr.update(value=0),  # qr_corner_radius
                            gr.update(value=""),  # header_text
                            gr.update(value=""),  # footer_text
                            gr.update(value=16),  # header_font_slider
                            gr.update(value=14),  # footer_font_slider
                            gr.update(value="Default"),  # header_font_select
                            gr.update(value=None),  # header_font_file
                            gr.update(value=False),  # header_bold
                            gr.update(value="center"),  # header_align
                            gr.update(value="Default"),  # footer_font_select
                            gr.update(value=None),  # footer_font_file
                            gr.update(value=False),  # footer_bold
                            gr.update(value="center"),  # footer_align
                            gr.update(value=t("settings_reset", lang)),
                            gr.update(value="square"),  # shape_dropdown
                            gr.update(value="Classic"),  # gradient_palette
                        )
                    except Exception:
                        logging.exception("Failed to reset settings")
                        return ()

                # Wire language selector to UI updater (many outputs)
                lang_select.change(
                    fn=_update_ui,
                    inputs=[lang_select],
                    outputs=[
                        title_md,
                        instr_md,
                        vcard_generate,
                        url_generate,
                        text_generate,
                        mail_generate,
                        phone_generate,
                        sms_generate,
                        wifi_generate,
                        evt_generate,
                        geo_generate,
                        app_generate,
                        pay_generate,
                        me_generate,
                        url_input,
                        text_input,
                        mail_to,
                        mail_subject,
                        mail_body,
                        phone_input,
                        sms_phone,
                        sms_message,
                        wifi_ssid,
                        wifi_auth,
                        wifi_password,
                        wifi_hidden,
                        evt_summary,
                        evt_start,
                        evt_end,
                        evt_location,
                        evt_description,
                        geo_lat,
                        geo_lon,
                        geo_label,
                        app_url,
                        pay_address,
                        pay_amount,
                        pay_label,
                        me_name,
                        me_tel,
                        me_email,
                        me_org,
                        me_note,
                        qr_customization_md,
                        size_slider,
                        ec_dropdown,
                        max_payload,
                        qr_border_md,
                        border_slider,
                        corner_radius,
                        qr_corner_radius,
                        border_color_picker,
                        qr_colours_md,
                        transparent_bg,
                        palette_dropdown,
                        custom_fg,
                        custom_bg,
                        qr_gradient_md,
                        gradient_toggle,
                        gradient_palette,
                        gradient_from,
                        gradient_to,
                        gradient_target,
                        gradient_angle,
                        qr_appearance_md,
                        shape_dropdown,
                        pattern_dropdown,
                        pattern_strength,
                        qr_files_md,
                        upload_batch_csv,
                        download_batch_btn,
                        download_template_btn,
                        logo_md,
                        shared_logo,
                        shared_logo_enable,
                        logo_preview,
                        logo_scale,
                        logo_opacity,
                        logo_clip,
                        qr_text_md,
                        header_text,
                        footer_text,
                        qr_header_md,
                        header_font_select,
                        header_font_slider,
                        header_font_file,
                        header_bold,
                        header_align,
                        qr_footer_md,
                        footer_font_select,
                        footer_font_slider,
                        footer_font_file,
                        footer_bold,
                        footer_align,
                        lang_select,
                        settings_status,
                        save_settings_btn,
                        reset_settings_btn,
                        shape_dropdown,
                        gradient_palette,
                    ],
                )

                # Wire button events to handlers using shared styling controls
                # New order: file, enable, palette, gradient toggle, gradient_target, gradient from/to, angle, custom fg/bg, shape, pattern, pattern_strength, logo_scale, logo_opacity, size, error_correction
                shared_inputs = [
                    shared_logo,
                    shared_logo_enable,
                    palette_dropdown,
                    transparent_bg,
                    gradient_toggle,
                    gradient_target,
                    gradient_from,
                    gradient_to,
                    gradient_angle,
                    custom_fg,
                    custom_bg,
                    shape_dropdown,
                    pattern_dropdown,
                    pattern_strength,
                    logo_scale,
                    logo_opacity,
                    logo_clip,
                    border_slider,
                    border_color_picker,
                    corner_radius,
                    qr_corner_radius,
                    header_text,
                    footer_text,
                    header_font_slider,
                    footer_font_slider,
                    header_font_select,
                    header_font_file,
                    header_bold,
                    header_align,
                    footer_font_select,
                    footer_font_file,
                    footer_bold,
                    footer_align,
                    size_slider,
                    ec_dropdown,
                    gradient_palette,
                ]

                # Connect Save / Reset buttons
                save_settings_btn.click(
                    fn=_save_settings,
                    inputs=shared_inputs,
                    outputs=[settings_preview_img, settings_status],
                )
                reset_settings_btn.click(
                    fn=_reset_to_defaults,
                    inputs=None,
                    outputs=[
                        size_slider,
                        ec_dropdown,
                        max_payload,
                        transparent_bg,
                        palette_dropdown,
                        gradient_toggle,
                        gradient_from,
                        gradient_to,
                        gradient_angle,
                        gradient_target,
                        custom_fg,
                        custom_bg,
                        shape_dropdown,
                        pattern_dropdown,
                        pattern_strength,
                        shared_logo_enable,
                        logo_preview,
                        logo_scale,
                        logo_opacity,
                        logo_clip,
                        border_slider,
                        border_color_picker,
                        corner_radius,
                        qr_corner_radius,
                        header_text,
                        footer_text,
                        header_font_slider,
                        footer_font_slider,
                        header_font_select,
                        header_font_file,
                        header_bold,
                        header_align,
                        footer_font_select,
                        footer_font_file,
                        footer_bold,
                        footer_align,
                        settings_status,
                        shape_dropdown,
                        gradient_palette,
                    ],
                )

                # Wire downloads
                download_batch_btn.click(
                    fn=_download_batch,
                    inputs=[upload_batch_csv] + shared_inputs,
                    outputs=[download_batch_file],
                )
                download_template_btn.click(
                    fn=_download_template,
                    inputs=None,
                    outputs=[upload_batch_csv],
                )

                palette_dropdown.change(
                    fn=_update_palette,
                    inputs=[palette_dropdown],
                    outputs=[custom_fg, custom_bg],
                )
                gradient_palette.change(
                    fn=_update_gradient_palette,
                    inputs=[gradient_palette],
                    outputs=[gradient_from, gradient_to],
                )
                shared_logo.change(
                    fn=_save_logo_and_preview,
                    inputs=[shared_logo],
                    outputs=[logo_preview],
                )

                vcard_generate.click(
                    fn=gen_vcard,
                    inputs=vcard_inputs + shared_inputs,
                    outputs=[vcard_preview_img, vcard_payload_preview],
                )

                url_generate.click(
                    fn=gen_url,
                    inputs=[url_input] + shared_inputs,
                    outputs=[url_preview_img, url_payload_preview],
                )
                text_generate.click(
                    fn=gen_text,
                    inputs=[text_input] + shared_inputs,
                    outputs=[text_preview_img, text_payload_preview],
                )
                mail_generate.click(
                    fn=gen_mailto,
                    inputs=[mail_to, mail_subject, mail_body] + shared_inputs,
                    outputs=[mail_preview_img, mail_payload_preview],
                )
                phone_generate.click(
                    fn=gen_tel,
                    inputs=[phone_input] + shared_inputs,
                    outputs=[phone_preview_img, phone_payload_preview],
                )
                sms_generate.click(
                    fn=gen_sms,
                    inputs=[sms_phone, sms_message] + shared_inputs,
                    outputs=[sms_preview_img, sms_payload_preview],
                )
                wifi_generate.click(
                    fn=gen_wifi,
                    inputs=[wifi_ssid, wifi_auth, wifi_password, wifi_hidden]
                    + shared_inputs,
                    outputs=[wifi_preview_img, wifi_payload_preview],
                )
                evt_generate.click(
                    fn=gen_event,
                    inputs=[
                        evt_summary,
                        evt_start,
                        evt_end,
                        evt_location,
                        evt_description,
                    ]
                    + shared_inputs,
                    outputs=[evt_preview_img, evt_payload_preview],
                )
                geo_generate.click(
                    fn=gen_geo,
                    inputs=[geo_lat, geo_lon, geo_label] + shared_inputs,
                    outputs=[geo_preview_img, geo_payload_preview],
                )
                app_generate.click(
                    fn=gen_applink,
                    inputs=[app_url] + shared_inputs,
                    outputs=[app_preview_img, app_payload_preview],
                )
                pay_generate.click(
                    fn=gen_payment,
                    inputs=[pay_address, pay_amount, pay_label] + shared_inputs,
                    outputs=[pay_preview_img, pay_payload_preview],
                )
                me_generate.click(
                    fn=gen_mecard,
                    inputs=[me_name, me_tel, me_email, me_org, me_note] + shared_inputs,
                    outputs=[me_preview_img, me_payload_preview],
                )

            demo.launch()
        except KeyboardInterrupt:
            logging.info("Exiting on keyboard interrupt.")
            sys.exit(0)
