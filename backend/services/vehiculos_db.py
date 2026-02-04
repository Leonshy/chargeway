import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "instance/vehiculos_ev.db"


def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn
