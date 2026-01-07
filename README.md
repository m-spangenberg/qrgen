# QR-vCard

<div align="center">
<img src="readme/readme_header_qrvcard.png" alt="example qr code" width="720"/>
</div>

## __Summary__

For my **CS50P** [Final Project](https://cs50.harvard.edu/python/2022/project/), I created a single-purpose application that generates vCards in QR code format. Originally built as a desktop app, it has since been migrated to a browser-based interface powered by **Gradio**.

## __Todo__

- [x] Migrate from Tkinter to Gradio
- [x] Add color customization for QR codes
- [x] Add logo/image overlay support
- [x] Improve field validation and error handling
- [x] Implement live preview of vCard and QR code
- [x] Update README with new setup instructions
- [x] Switch to `uv` for dependency management
- [x] Add tests for new features
- [] Expand to support additional QR formats (e.g., WiFi, URLs)
- [] Add configuration saving/loading for user preferences
- [] Add additional styling options for QR codes (shapes, patterns)
- [] Add colour palletes and gradients for QR codes
- [] Add multi-language support for the interface
- [] Deploy to a public web server for easy access

## __Description__

This application allows users to enter contact details into a responsive web interface to generate a high-quality Quick Response (QR) code. These codes can be scanned by most modern mobile devices, making them ideal for embedding contact details on business cards, resumes, or marketing materials.

The migration to Gradio brings several key improvements:
- **Responsive Web UI**: Access the tool via your browser with a modern look and feel.
- **Customization**: Change QR foreground and background colors to match your branding.
- **Branding**: Upload a logo or image to overlay in the center of the QR code.
- **Robust Validation**: Real-time feedback on field formats (Email, Phone, Birthday, etc.).
- **Live Preview**: See your vCard string and QR code update as you generate.

### __Setup__

The project now uses **uv** for extremely fast and reliable dependency management. Make use of this one-liner for a quick setup.

```bash
git clone https://github.com/m-spangenberg/qr-vcard-generator && cd qr-vcard-generator/ && make init
```

Alternatively, you can manually set up the environment:

```bash
# Clone the repository
git clone https://github.com/m-spangenberg/qr-vcard-generator
cd qr-vcard-generator/

# Sync dependencies
uv sync

# Launch the Gradio web interface
uv run python main.py
```

### __vCard Format__

The vCard, or otherwise known as the VCF (Virtual Contact File) format is essentially a container format for contact information that can be shared between electronic devices, notably mobile phones.

With every entry on a new line, the `.vcf` format must always begin with `BEGIN:VCARD`, followed immediately by the version identifier `VERSION:4.0`, and must end with `END:VCARD`.

#### Example layout

```bash
BEGIN:VCARD
VERSION:4.0
KIND:individual
EMAIL;TYPE=work:j.appleseed@acmeappleco.bar
EMAIL;TYPE=work:j.appleseed@foo.bar
TITLE:Apple Seed Distributor
ROLE:Project Leader
FN:Johnny Appleseed
BDAY:19850412
ADR;TYPE=HOME:pobox;ext;street;locality;region;code;country
TEL;TYPE=CELL:+123 12 123 1234
TEL;TYPE=WORK:+123 12 12 1234
TEL;TYPE=HOME:+123 12 12 1234
TEL;TYPE=FAX:+123 12 12 1234
URL: https://www.example.com
TZ: Africa/Windhoek
ORG: ACME Apple Co. - Will take precedence over Full Name.
NOTE: optional note, keep it short
END:VCARD
```

#### Example QR Code

<div align="center">
<img src="readme/example.png" alt="example qr code" width="240"/>
</div>  

### __Testing and Development__

To set up the environment and install all dependencies:

``` bash
make init
```

To perform unittests with `pytest`:

``` bash
make test
```

Or manually using `uv`:

```bash
# Perform unittests
uv run pytest
```

### __Acknowledgements__

Thank you to David Malan and his entire team for helping to make Harvard's CS50 accessible to anyone who wants to learn.

#### __Further Reading__

If you intend to fork this project, see the following links for helpful information on vCards.

* [Internet Engineering Task Force](https://datatracker.ietf.org/doc/html/rfc6350) - Format Specification
* [World Wide Web Consortium](https://www.w3.org/2002/12/cal/vcard-notes.html) - Format Notes
* [Wikipedia](https://en.wikipedia.org/wiki/VCard) - vCards

#### __Libraries Used__

The following libraries and tools are used to make this project possible:

* [Gradio](https://gradio.app/) - Modern web interface framework
* [qrcode](https://pypi.org/project/qrcode/) - Generating high-quality QR codes
* [Pillow](https://pypi.org/project/Pillow/) - Image processing and branding support
* [uv](https://github.com/astral-sh/uv) - Fast Python package management
