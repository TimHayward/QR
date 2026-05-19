import base64
from flask import (
    Flask, render_template, request, redirect, url_for,
    send_file, abort, flash
)
import io
import db
from qr_generator import (
    generate_qr_image, build_qr_data,
    COLOR_SCHEMES, FRAME_STYLES
)

app = Flask(__name__)
app.secret_key = "qr-app-secret-key-change-in-production"

db.init_db()

TEMPLATES = [
    ("website",  "Website"),
    ("vcard",    "Digital Business Card"),
    ("linkedin", "LinkedIn Profile"),
    ("wifi",     "Wi-Fi"),
    ("text",     "Text"),
]

LOGOS = [
    ("none",     "None"),
    ("linkedin", "LinkedIn"),
    ("wifi",     "Wi-Fi"),
    ("custom",   "Custom Upload"),
]

ERROR_LEVELS = [
    ("L", "Low (7%)"),
    ("M", "Medium (15%)"),
    ("Q", "Quartile (25%)"),
    ("H", "High (30%)"),
]


@app.route("/")
def index():
    return render_template(
        "index.html",
        templates=TEMPLATES,
        logos=LOGOS,
        error_levels=ERROR_LEVELS,
        color_schemes=COLOR_SCHEMES,
        frame_styles=FRAME_STYLES,
    )


@app.route("/generate", methods=["POST"])
def generate():
    form = request.form
    template_type = form.get("template_type", "text")
    name = form.get("name", "").strip() or template_type.capitalize()

    # Colour
    scheme = form.get("color_scheme", "classic")
    if scheme == "custom":
        fg_color = form.get("custom_fg", "#000000")
        bg_color = form.get("custom_bg", "#FFFFFF")
    else:
        fg_color, bg_color = COLOR_SCHEMES.get(scheme, ("#000000", "#FFFFFF"))

    frame_style = form.get("frame_style", "none")
    frame_text = form.get("frame_text", "Scan Me")
    logo = form.get("logo", "none")
    error_correction = form.get("error_correction", "M")

    # Auto-default logo for template types
    if logo == "auto":
        if template_type == "linkedin":
            logo = "linkedin"
        elif template_type == "wifi":
            logo = "wifi"
        else:
            logo = "none"

    # Build QR data from template fields
    qr_data = build_qr_data(template_type, form)
    if not qr_data:
        flash("Please fill in the required fields.", "error")
        return redirect(url_for("index"))

    # Generate image
    image_bytes = generate_qr_image(
        qr_data, fg_color, bg_color,
        frame_style, frame_text, logo, error_correction
    )

    # Save to DB
    qr_id = db.save_qr_code(
        name, template_type, qr_data, fg_color, bg_color,
        frame_style, frame_text, logo, error_correction, image_bytes
    )

    return redirect(url_for("view_qr", qr_id=qr_id))


@app.route("/qr/<int:qr_id>")
def view_qr(qr_id):
    qr = db.get_qr_code(qr_id)
    if not qr:
        abort(404)
    img_b64 = base64.b64encode(qr["image_data"]).decode()
    return render_template("view.html", qr=qr, img_b64=img_b64)


@app.route("/qr/<int:qr_id>/download")
def download_qr(qr_id):
    qr = db.get_qr_code(qr_id)
    if not qr:
        abort(404)
    return send_file(
        io.BytesIO(qr["image_data"]),
        mimetype="image/png",
        as_attachment=True,
        download_name=f"{qr['name']}.png",
    )


@app.route("/qr/<int:qr_id>/delete", methods=["POST"])
def delete_qr(qr_id):
    db.delete_qr_code(qr_id)
    flash("QR code deleted.", "info")
    return redirect(url_for("list_qr"))


@app.route("/list")
def list_qr():
    qr_codes = db.get_all_qr_codes()
    return render_template("list.html", qr_codes=qr_codes)


@app.route("/qr/<int:qr_id>/image")
def qr_image(qr_id):
    qr = db.get_qr_code(qr_id)
    if not qr:
        abort(404)
    return send_file(io.BytesIO(qr["image_data"]), mimetype="image/png")


if __name__ == "__main__":
    app.run(debug=True)
