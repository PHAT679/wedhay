# file: database.py
import pyodbc
from flask import g
from config import Config


def get_db() -> pyodbc.Connection:
    """Trả về connection gắn vào Flask g (per-request)."""
    if "db" not in g:
        try:
            g.db = pyodbc.connect(Config.connection_string(), autocommit=False)
        except pyodbc.Error as e:
            print(f"[DB] Lỗi kết nối: {e}")
            raise ConnectionError("Không thể kết nối cơ sở dữ liệu.") from e
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass


def init_app(app):
    """Đăng ký close_db vào Flask teardown."""
    app.teardown_appcontext(close_db)
