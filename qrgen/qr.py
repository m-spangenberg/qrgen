import qrcode
import os
import logging
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageOps
import textwrap

def _normalize_color(color):
    if color is None:
        return None
    if not isinstance(color, str):
        return color
    color = color.strip()
    if not color:
        return None
    
    # Check if it's already a hex starting with #
    if color.startswith("#"):
        return color
        
    # Check if it's a known color name (basic list, PIL handles the rest)
    if color.lower() in ("white", "black", "red", "green", "blue", "yellow", "cyan", "magenta", "transparent"):
        return color.lower()

    # Could be a hex without # (3 or 6 chars)
    if len(color) in (3, 6) and all(c in "0123456789abcdefABCDEF" for c in color):
        return f"#{color}"
        
    return color

def _to_rgb_tuple(color, default=(0, 0, 0)):
    if isinstance(color, (tuple, list)):
        return tuple(color)
    
    normalized = _normalize_color(color)
    if normalized is None:
        return default
        
    from PIL import ImageColor
    try:
        return ImageColor.getrgb(normalized)
    except Exception as e:
        logging.log(logging.DEBUG, f"Failed to resolve color '{color}': {e}")
        return default

def generate_qr(
    data,
    dest="output/preview.png",
    size=512,
    fill_color="black",
    back_color="white",
    border=0,
    corner_radius=0,
    qr_corner_radius=None,
    border_corner_radius=None,
    border_color=None,
    logo_path=None,
    logo_scale=0.2,
    logo_opacity=1.0,
    logo_clip="none",
    transparent_bg=False,
    module_drawer="square",
    color_mask="solid",
    gradient_type="linear",
    gradient_start="#000000",
    gradient_end="#ffffff",
    gradient_angle=0,
    gradient_target="foreground",
    header_text=None,
    footer_text=None,
    header_font_size=24,
    footer_font_size=18,
    header_align="center",
    footer_align="center",
    header_bold=True,
    footer_bold=False,
    header_font_path=None,
    footer_font_path=None,
    **kwargs,
):
    import qrcode
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers import (
        SquareModuleDrawer,
        GappedSquareModuleDrawer,
        CircleModuleDrawer,
        RoundedModuleDrawer,
        VerticalBarsDrawer,
        HorizontalBarsDrawer,
    )
    from PIL import Image, ImageDraw, ImageChops, ImageOps
    import textwrap

    # Map legacy or GUI-specific names
    error_correction = kwargs.get("error_correction", "H")
    ec_map = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H,
    }
    ec_level = ec_map.get(str(error_correction).upper(), qrcode.constants.ERROR_CORRECT_H)

    # Resolve palette if provided
    if "palette" in kwargs:
        from .styles import resolve_palette

        fill_color, back_color = resolve_palette(
            kwargs["palette"], fill_color, back_color
        )

    # If GUI sends 'shape', use it for module_drawer
    if "shape" in kwargs:
        module_drawer = kwargs["shape"]
    
    # If GUI sends 'gradient' as a dict
    if "gradient" in kwargs and kwargs["gradient"]:
        color_mask = "gradient"
        g = kwargs["gradient"]
        if isinstance(g, dict):
            gradient_start = g.get("colors", ["#000000", "#ffffff"])[0]
            gradient_end = g.get("colors", ["#000000", "#ffffff"])[1]
            gradient_angle = g.get("angle", 0)
            gradient_target = g.get("target", "foreground")

    drawer_map = {
        "square": SquareModuleDrawer(),
        "gapped": GappedSquareModuleDrawer(),
        "circle": CircleModuleDrawer(),
        "rounded": RoundedModuleDrawer(),
        "vertical": VerticalBarsDrawer(),
        "horizontal": HorizontalBarsDrawer(),
    }
    drawer = drawer_map.get(module_drawer.lower(), SquareModuleDrawer())

    qr = qrcode.QRCode(error_correction=ec_level)
    qr.add_data(data)
    qr.make(fit=True)

    # High-res intermediate
    img = qr.make_image(image_factory=StyledPilImage, module_drawer=drawer, eye_drawer=drawer).convert("RGBA")
    mask = ImageOps.invert(img.convert("L"))
    pixel_size = img.width
    resample = Image.LANCZOS

    # Background / Foreground
    if transparent_bg:
        bg_rgba = (0, 0, 0, 0)
        bg_img = Image.new("RGBA", (pixel_size, pixel_size), bg_rgba)
    else:
        bg_rgba = _to_rgb_tuple(back_color, default=(255, 255, 255))[:3]
        bg_img = Image.new("RGBA", (pixel_size, pixel_size), bg_rgba + (255,))
    
    fg_rgba = _to_rgb_tuple(fill_color, default=(0, 0, 0))[:3]
    fg_img = Image.new("RGBA", (pixel_size, pixel_size), fg_rgba + (255,))

    if color_mask == "gradient" and not transparent_bg:
        grad_base = Image.new("RGBA", (pixel_size, pixel_size))
        c1 = _to_rgb_tuple(gradient_start, default=(0, 0, 0))[:3]
        c2 = _to_rgb_tuple(gradient_end, default=(255, 255, 255))[:3]
        for y in range(pixel_size):
            t = y / max(1, pixel_size - 1)
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b_ = int(c1[2] + (c2[2] - c1[2]) * t)
            for x in range(pixel_size): grad_base.putpixel((x, y), (r, g, b_, 255))
        
        angle = float(gradient_angle or 0)
        # Use BICUBIC for rotation as LANCZOS is not supported by Pillow's rotate()
        rotated_grad = grad_base.rotate(90 - angle, resample=Image.BICUBIC, expand=False)
        if gradient_target == "background":
            bg_img = rotated_grad
        else:
            fg_img = rotated_grad

    # Compose QR
    img = Image.composite(fg_img, bg_img, mask)
    if img.width != size:
        img = img.resize((size, size), resample)

    # Post-processing
    try:
        b = max(0, int(border or 0))
        qr_cr = max(0, int(qr_corner_radius if qr_corner_radius is not None else corner_radius))
        outer_cr = max(0, int(border_corner_radius if border_corner_radius is not None else corner_radius))
        
        # Determine background color for border fallback
        actual_back_color = back_color
        if color_mask == "gradient" and gradient_target == "background":
            # If background is a gradient, we can't easily pick one color for the border.
            # Using gradient_start as a reasonable fallback for the border if not specified.
            actual_back_color = gradient_start
            
        b_color = _normalize_color(border_color) if border_color else actual_back_color
        
        from PIL import ImageFont
        def _get_fnt(p, s, bold):
            if p:
                try: return ImageFont.truetype(p, s)
                except: pass
            try: return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", s)
            except: return ImageFont.load_default()

        hf = _get_fnt(header_font_path, header_font_size, header_bold)
        ff = _get_fnt(footer_font_path, footer_font_size, footer_bold)

        def _draw_txt(dr, txt, fnt, al, y, cw, clr):
            if not txt or not fnt: return 0
            pw = cw - (b * 2) - 16
            ls = textwrap.wrap(txt, width=max(1, int(pw / (header_font_size * 0.5))))
            cy = y
            for l in ls:
                try: bb = dr.textbbox((0, 0), l, font=fnt); lw, lh = bb[2]-bb[0], bb[3]-bb[1]
                except: lw, lh = 0, header_font_size
                tx = b+8 if al=="left" else (cw-b-8-lw if al=="right" else (cw-lw)//2)
                dr.text((tx, cy), l, fill=clr, font=fnt)
                cy += lh + 2
            return cy - y

        def _est_h(txt, fnt, cw):
            if not txt or not fnt: return 0
            pw = cw - (b * 2) - 16
            ls = textwrap.wrap(txt, width=max(1, int(pw / (header_font_size * 0.5))))
            return len(ls) * (header_font_size + 4) + 8

        nw = img.width + b * 2
        hh = _est_h(header_text, hf, nw)
        fh = _est_h(footer_text, ff, nw)
        nh = img.height + b * 2 + hh + fh
        
        # Use appropriate fallbacks for border color (bg if not specified)
        actual_back_color = back_color if back_color else "white"
        if color_mask == "gradient" and gradient_target == "background" and not transparent_bg:
            actual_back_color = gradient_start if gradient_start else "white"
            
        b_color = border_color if border_color else actual_back_color
        
        if transparent_bg:
            canvas = Image.new("RGBA", (nw, nh), (0, 0, 0, 0))
        else:
            canvas = Image.new("RGBA", (nw, nh), _to_rgb_tuple(b_color, default=(255, 255, 255))[:3] + (255,))
        
        px, py = b, b + hh
        
        # QR Corner Rounding
        if qr_cr > 0:
            qm = Image.new("L", (img.width, img.height), 0)
            ImageDraw.Draw(qm).rounded_rectangle([0, 0, img.width, img.height], radius=qr_cr, fill=255)
            canvas.paste(img, (px, py), mask=qm)
        else:
            canvas.paste(img, (px, py))

        dc = ImageDraw.Draw(canvas)
        tc = _to_rgb_tuple(fill_color, default=(0, 0, 0))
        if header_text: _draw_txt(dc, header_text, hf, header_align.lower(), 4, nw, tc)
        if footer_text: _draw_txt(dc, footer_text, ff, footer_align.lower(), py + img.height + b + 4, nw, tc)

        # Outer Rounding
        if outer_cr > 0:
            om = Image.new("L", (nw, nh), 0)
            ImageDraw.Draw(om).rounded_rectangle([0, 0, nw, nh], radius=outer_cr, fill=255)
            canvas.putalpha(om)

        # Logo
        if logo_path and os.path.isfile(logo_path):
            logo = Image.open(logo_path).convert("RGBA")
            lsz = max(1, int(size * float(logo_scale or 0.2)))
            logo = logo.resize((lsz, lsz), resample)
            
            # Apply opacity to the logo first
            if float(logo_opacity or 1.0) < 1.0:
                alpha = logo.split()[-1].point(lambda p: int(p * float(logo_opacity)))
                logo.putalpha(alpha)
                
            lx, ly = px + (img.width - lsz)//2, py + (img.height - lsz)//2
            
            if logo_clip != "none":
                # Create a larger cutout mask
                buffer = max(2, int(lsz * 0.1))
                csz = lsz + buffer * 2
                cutout_mask = Image.new("L", (csz, csz), 0)
                draw = ImageDraw.Draw(cutout_mask)
                if logo_clip == "circle":
                    draw.ellipse([0, 0, csz, csz], fill=255)
                else:
                    draw.rounded_rectangle([0, 0, csz, csz], radius=max(1, int(buffer*0.5)), fill=255)
                
                clx, cly = px + (img.width - csz)//2, py + (img.height - csz)//2
                canvas.paste((0,0,0,0), (clx, cly), mask=cutout_mask)
                
                # Clip the logo itself if requested
                lm = Image.new("L", (lsz, lsz), 0)
                if logo_clip == "circle":
                    ImageDraw.Draw(lm).ellipse([0, 0, lsz, lsz], fill=255)
                else:
                    ImageDraw.Draw(lm).rectangle([0, 0, lsz, lsz], fill=255)
                
                # Combine logo mask with opacity
                if float(logo_opacity or 1.0) < 1.0:
                    lm = lm.point(lambda p: int(p * float(logo_opacity)))
                logo.putalpha(lm)

            canvas.paste(logo, (lx, ly), mask=logo.split()[-1])
        img = canvas
    except Exception:
        logging.exception("Post-processing failure")

    img.save(dest)
