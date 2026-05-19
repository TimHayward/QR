import sqlite3
import json
from datetime import datetime

DB_PATH = "qrcodes.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS qr_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                template_type TEXT NOT NULL,
                data TEXT NOT NULL,
                fg_color TEXT NOT NULL DEFAULT '#000000',
                bg_color TEXT NOT NULL DEFAULT '#FFFFFF',
                frame_style TEXT NOT NULL DEFAULT 'none',
                frame_text TEXT NOT NULL DEFAULT 'Scan Me',
                logo TEXT NOT NULL DEFAULT 'none',
                error_correction TEXT NOT NULL DEFAULT 'M',
                image_data BLOB,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()


def save_qr_code(name, template_type, data, fg_color, bg_color,
                 frame_style, frame_text, logo, error_correction, image_data):
    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO qr_codes
               (name, template_type, data, fg_color, bg_color, frame_style,
                frame_text, logo, error_correction, image_data, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, template_type, data, fg_color, bg_color,
             frame_style, frame_text, logo, error_correction, image_data,
             datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        return cursor.lastrowid


def get_all_qr_codes():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, name, template_type, fg_color, bg_color, "
            "frame_style, frame_text, logo, error_correction, created_at "
            "FROM qr_codes ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def get_qr_code(qr_id):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM qr_codes WHERE id = ?", (qr_id,)
        ).fetchone()
        return dict(row) if row else None


def delete_qr_code(qr_id):
    with get_db() as conn:
        conn.execute("DELETE FROM qr_codes WHERE id = ?", (qr_id,))
        conn.commit()
