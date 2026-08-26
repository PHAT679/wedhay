# file: config.py
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "seller-mgmt-secret-2024")

    # ── SQL Server ──────────────────────────────────────────────────────
    SERVER   = os.environ.get("SQL_SERVER",   "localhost")        # hoặc .\SQLEXPRESS
    DATABASE = os.environ.get("SQL_DATABASE", "QL_BAN_HANG_SAUBANH")
    DRIVER   = os.environ.get("SQL_DRIVER",   "ODBC Driver 17 for SQL Server")

    # Windows Authentication (để trống USERNAME / PASSWORD)
    USERNAME = os.environ.get("SQL_USERNAME", "")
    PASSWORD = os.environ.get("SQL_PASSWORD", "")
    TRUSTED  = os.environ.get("SQL_TRUSTED",  "yes")  # yes = Windows Auth

    @classmethod
    def connection_string(cls) -> str:
        if cls.TRUSTED.lower() == "yes":
            return (
                f"DRIVER={{{cls.DRIVER}}};"
                f"SERVER={cls.SERVER};"
                f"DATABASE={cls.DATABASE};"
                f"Trusted_Connection=yes;"
            )
        return (
            f"DRIVER={{{cls.DRIVER}}};"
            f"SERVER={cls.SERVER};"
            f"DATABASE={cls.DATABASE};"
            f"UID={cls.USERNAME};"
            f"PWD={cls.PASSWORD};"
        )
