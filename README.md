# QR Code Generator

A simple Flask web application for creating, customising, and saving QR codes.

## Features

- **5 Templates**: Website, Digital Business Card (vCard), LinkedIn Profile, Wi-Fi, Text
- **8 Colour Schemes**: Classic, Dark, Blue, Green, Red, Purple, Ocean, Sunset, and custom colour picker
- **5 Frame Styles**: None, Simple Border, Rounded Border, Banner Top, Banner Bottom — with editable header text (e.g. "Scan Me")
- **Logo Overlay**: None, LinkedIn (defaults for LinkedIn template), Wi-Fi (defaults for Wi-Fi template), or Auto (template default)
- **4 Error Correction Levels**: Low (7%), Medium (15%), Quartile (25%), High (30%)
- **SQLite Storage**: All generated QR codes are saved to a local SQLite database
- **Download**: Save any QR code as a PNG file

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

## Tech Stack

- **Backend**: Python / Flask
- **QR Generation**: `qrcode` + `Pillow`
- **Database**: SQLite (via Python `sqlite3`)
- **Frontend**: HTML5 / CSS3 / Vanilla JavaScript
