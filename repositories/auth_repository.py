# file: repositories/auth_repository.py
from .base_repository import BaseRepository
import pyodbc

class AuthRepository(BaseRepository):

    def login(self, username: str, password: str) -> dict | None:
        """Gọi usp_DANG_NHAP bằng pyodbc: EXEC usp_DANG_NHAP ?, ?"""
        try:
            print(f"[AuthRepository] calling usp_DANG_NHAP with username={username!r}")
            rows = self.fetch_procedure("usp_DANG_NHAP", [username, password])
            try:
                print("LOGIN RAW RESULT:", str(rows).encode("utf-8", "replace").decode("utf-8"))
            except Exception:
                pass
            if not rows:
                print("[AuthRepository] usp_DANG_NHAP returned 0 rows (check username/password/hash/is_active).")
            return rows[0] if rows else None
        except pyodbc.Error as e:
            print(f"[AuthRepository] Database error: {e}")
            raise e
