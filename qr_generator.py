import io
import os
import math
import qrcode
from qrcode.constants import (
    ERROR_CORRECT_L,
    ERROR_CORRECT_M,
    ERROR_CORRECT_Q,
    ERROR_CORRECT_H,
)
from PIL import Image, ImageDraw, ImageFont

LOGO_DIR = os.path.join(os.path.dirname(__file__), "static", "logos")

ERROR_CORRECTION_MAP = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}

# Predefined colour schemes: (name, fg, bg)
COLOR_SCHEMES = {
    "classic":   ("#000000", "#FFFFFF"),
    "dark":      ("#FFFFFF", "#1a1a2e"),
    "blue":      ("#FFFFFF", "#0a3d91"),
    "green":     ("#FFFFFF", "#1a6b1a"),
    "red":       ("#FFFFFF", "#a80000"),
    "purple":    ("#FFFFFF", "#4b0082"),
    "ocean":     ("#003366", "#e8f4fd"),
    "sunset":    ("#7b0000", "#fff3e0"),
    "custom":    None,
}

FRAME_STYLES = ["none", "simple", "rounded", "banner_top", "banner_bottom"]


def _load_logo(logo_name: str) -> Image.Image | None:
    """Load a logo image by name from the logos directory."""
    if not logo_name or logo_name == "none":
        return None
    path = os.path.join(LOGO_DIR, f"{logo_name}.png")
    if os.path.exists(path):
        return Image.open(path).convert("RGBA")
    return None


def _overlay_logo(qr_img: Image.Image, logo: Image.Image) -> Image.Image:
    """Overlay a logo in the centre of the QR code."""
    qr_size = qr_img.size[0]
    logo_max = int(qr_size * 0.22)
    logo = logo.copy()
    logo.thumbnail((logo_max, logo_max), Image.LANCZOS)

    # White circular background for the logo
    pad = 6
    bg_size = logo.size[0] + pad * 2
    bg = Image.new("RGBA", (bg_size, bg_size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(bg)
    draw.ellipse((0, 0, bg_size - 1, bg_size - 1), fill=(255, 255, 255, 255))

    offset = ((bg_size - logo.size[0]) // 2, (bg_size - logo.size[1]) // 2)
    bg.paste(logo, offset, logo)

    pos = ((qr_size - bg_size) // 2, (qr_size - bg_size) // 2)
    result = qr_img.convert("RGBA")
    result.paste(bg, pos, bg)
    return result.convert("RGB")


def _apply_frame(img: Image.Image, frame_style: str, frame_text: str,
                 fg_color: str, bg_color: str) -> Image.Image:
    """Wrap the QR image in a decorative frame with optional text."""
    if frame_style == "none":
        return img

    qr_w, qr_h = img.size
    border = 16
    font_size = 22
    text_gap = 8

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    # Measure text
    dummy = Image.new("RGB", (1, 1))
    draw_dummy = ImageDraw.Draw(dummy)
    bbox = draw_dummy.textbbox((0, 0), frame_text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    canvas_w = qr_w + border * 2
    extra_h = text_h + text_gap * 2 if frame_text else 0

    if frame_style in ("banner_top",):
        canvas_h = qr_h + border * 2 + extra_h
        canvas = Image.new("RGB", (canvas_w, canvas_h), bg_color)
        if frame_style == "rounded":
            _draw_rounded_rect(canvas, canvas_w, canvas_h, bg_color, fg_color)
        else:
            draw = ImageDraw.Draw(canvas)
            draw.rectangle([0, 0, canvas_w - 1, canvas_h - 1], outline=fg_color, width=3)
        # Text at top
        draw = ImageDraw.Draw(canvas)
        tx = (canvas_w - text_w) // 2
        ty = border // 2 + text_gap
        draw.text((tx, ty), frame_text, fill=fg_color, font=font)
        canvas.paste(img, (border, border + extra_h))
    else:
        # banner_bottom, simple, rounded – text below (or no text for simple)
        canvas_h = qr_h + border * 2 + (extra_h if frame_style != "simple" else 0)
        canvas = Image.new("RGB", (canvas_w, canvas_h), bg_color)
        draw = ImageDraw.Draw(canvas)

        if frame_style == "rounded":
            _draw_rounded_rect(draw, canvas_w, canvas_h, bg_color, fg_color)
        else:
            draw.rectangle([0, 0, canvas_w - 1, canvas_h - 1], outline=fg_color, width=3)

        canvas.paste(img, (border, border))

        if frame_style != "simple" and frame_text:
            tx = (canvas_w - text_w) // 2
            ty = qr_h + border + text_gap
            draw.text((tx, ty), frame_text, fill=fg_color, font=font)

    return canvas


def _draw_rounded_rect(draw: ImageDraw.ImageDraw, w: int, h: int,
                       bg_color: str, fg_color: str, radius: int = 20):
    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius,
                            outline=fg_color, fill=bg_color, width=3)


def build_qr_data(template_type: str, form: dict) -> str:
    """Convert template form fields into a QR data string."""
    if template_type == "website":
        url = form.get("url", "").strip()
        if url and not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url

    if template_type == "text":
        return form.get("text", "").strip()

    if template_type == "linkedin":
        username = form.get("linkedin_username", "").strip()
        if username.startswith("http"):
            return username
        return f"https://www.linkedin.com/in/{username}"

    if template_type == "wifi":
        ssid = form.get("ssid", "")
        password = form.get("password", "")
        encryption = form.get("encryption", "WPA")
        hidden = "true" if form.get("hidden") else "false"
        return f"WIFI:T:{encryption};S:{ssid};P:{password};H:{hidden};;"

    if template_type == "vcard":
        name = form.get("full_name", "")
        org = form.get("organization", "")
        title = form.get("job_title", "")
        email = form.get("email", "")
        phone = form.get("phone", "")
        url = form.get("website", "")
        address = form.get("address", "")
        parts = ["BEGIN:VCARD", "VERSION:3.0", f"FN:{name}"]
        if org or title:
            parts.append(f"ORG:{org}")
            parts.append(f"TITLE:{title}")
        if email:
            parts.append(f"EMAIL:{email}")
        if phone:
            parts.append(f"TEL:{phone}")
        if url:
            parts.append(f"URL:{url}")
        if address:
            parts.append(f"ADR:;;{address};;;;")
        parts.append("END:VCARD")
        return "\n".join(parts)

    return form.get("data", "")


def generate_qr_image(data: str, fg_color: str, bg_color: str,
                      frame_style: str, frame_text: str,
                      logo_name: str, error_correction: str) -> bytes:
    """Generate a QR code PNG and return raw bytes."""
    ec = ERROR_CORRECTION_MAP.get(error_correction.upper(), ERROR_CORRECT_M)

    qr = qrcode.QRCode(
        version=None,
        error_correction=ec,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert("RGB")

    # Overlay logo
    logo_img = _load_logo(logo_name)
    if logo_img:
        img = _overlay_logo(img, logo_img)

    # Apply frame
    img = _apply_frame(img, frame_style, frame_text, fg_color, bg_color)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
