"""
gui.py: GUI logic for QR vCard Generator
"""

import logging
import sys

import gradio as gr
import qrcode
import qrcode.image.svg

from .qr import generate_qr
from .validation import (
    validate_address,
    validate_birthday,
    validate_email,
    validate_note,
    validate_phone,
    validate_required,
    validate_url,
)
from .vcard import DEFAULT_VCARD_FIELDS, build_vcard


class QRVCardGUI:
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
        Launch the Gradio interface for the QR vCard Generator.
        Sets up the layout, color pickers, logo upload, and preview area.
        """
        try:
            def gradio_generate_qr(*args):
                # Extract inputs
                # args: [field1, field2, ..., logo_file, fg_color, bg_color]
                num_fields = len(self.user_fields)
                user_data = {
                    self.user_fields[i]: args[i]
                    for i in range(num_fields)
                    if args[i]
                }
                
                logo_file = args[num_fields]
                fg_color = args[num_fields + 1]
                bg_color = args[num_fields + 2]

                # Validation
                validation_map = {
                    "FN": (validate_required, "Full Name is required."),
                    "EMAIL": (validate_email, "Invalid email format."),
                    "TEL": (validate_phone, "Invalid phone number format."),
                    "BDAY": (validate_birthday, "Birthday must be YYYYMMDD."),
                    "ADR": (validate_address, "Address needs at least 3 parts separated by ';'."),
                    "URL": (validate_url, "Invalid URL format."),
                    "NOTE": (validate_note, "Note is too long (max 200 chars)."),
                }

                for field, value in user_data.items():
                    for key, (func, msg) in validation_map.items():
                        if key in field:
                            if not func(value):
                                gr.Warning(f"Validation error in {field}: {msg}")
                                return None, f"Error: {msg}"

                vcard_str = build_vcard(user_data)
                
                # Easter Egg: If no user data is provided, point to Rick Astley
                qr_content = vcard_str
                if not user_data:
                    qr_content = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

                logo_path = None
                if logo_file:
                    logo_path = logo_file.name

                generate_qr(
                    qr_content, 
                    logo_path=logo_path, 
                    size=240, 
                    fill_color=fg_color, 
                    back_color=bg_color
                )
                return "output/preview.png", vcard_str

            def reset_inputs():
                # Returns: resets for inputs + color pickers + output image + preview text
                return [None] * (len(self.user_fields) + 1) + ["#000000", "#ffffff"] + ["images/placeholder.png", ""]

            with gr.Blocks(title="QR vCard Generator") as demo:
                gr.Markdown("# QR vCard Generator")
                gr.Markdown("Fill in the details below to generate a vCard QR code. You can also customize the colors and add a logo.")
                with gr.Row():
                    with gr.Column():
                        input_widgets = []
                        for field in self.user_fields:
                            input_widgets.append(
                                gr.Textbox(
                                    label=field, 
                                    placeholder=DEFAULT_VCARD_FIELDS[field],
                                    info=self.field_descriptions.get(field, "")
                                )
                            )
                        
                        with gr.Row():
                            fg_color = gr.ColorPicker(label="QR Color", value="#000000")
                            bg_color = gr.ColorPicker(label="Background Color", value="#ffffff")
                        
                        logo_upload = gr.File(label="Choose Logo/Image Overlay")
                        
                        with gr.Row():
                            generate_btn = gr.Button("Generate QR Code", variant="primary")
                            clear_btn = gr.Button("Clear All")

                    with gr.Column():
                        qr_code_output = gr.Image(label="QR Code Preview", value="images/placeholder.png")
                        vcard_preview = gr.Textbox(label="vCard Preview", lines=15)

                # Events
                generate_btn.click(
                    fn=gradio_generate_qr,
                    inputs=input_widgets + [logo_upload, fg_color, bg_color],
                    outputs=[qr_code_output, vcard_preview],
                )

                clear_btn.click(
                    fn=reset_inputs,
                    inputs=[],
                    outputs=input_widgets + [logo_upload, fg_color, bg_color, qr_code_output, vcard_preview],
                )

            demo.launch()
                       
        except KeyboardInterrupt:
            logging.info("Exiting on keyboard interrupt.")
            sys.exit(0)