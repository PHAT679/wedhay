# file: repositories/base_repository.py
#import pyodbc
from database import get_db


class BaseRepository:
    """Lớp cơ sở: toàn bộ truy cập DB đi qua đây."""

    # ── helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _rows_to_dicts(cursor) -> list[dict]:
        if cursor.description is None:
            return []
        cols = [c[0] for c in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def _conn(self) -> pyodbc.Connection:
        return get_db()

    # ── Views ──────────────────────────────────────────────────────────

    def fetch_view(self, view_name: str) -> list[dict]:
        """SELECT * FROM <view>"""
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.execute(f"SELECT * FROM {view_name}")
            return self._rows_to_dicts(cur)
        except pyodbc.Error as e:
            print(f"[DB] fetch_view({view_name}): {e}")
            return []
        finally:
            cur.close()

    def fetch_view_where(self, view_name: str, where: str, params: list) -> list[dict]:
        """SELECT * FROM <view> WHERE <where_clause>"""
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.execute(f"SELECT * FROM {view_name} WHERE {where}", params)
            return self._rows_to_dicts(cur)
        except pyodbc.Error as e:
            print(f"[DB] fetch_view_where({view_name}): {e}")
            return []
        finally:
            cur.close()

    # ── Stored Procedures ──────────────────────────────────────────────

    def fetch_procedure(self, proc: str, params: list = None) -> list[dict]:
        """EXEC proc — trả dữ liệu."""
        conn = self._conn()
        cur = conn.cursor()
        try:
            if params:
                ph = ", ".join(["?"] * len(params))
                cur.execute(f"SET NOCOUNT ON; EXEC {proc} {ph}", params)
            else:
                cur.execute(f"SET NOCOUNT ON; EXEC {proc}")
            return self._rows_to_dicts(cur)
        except pyodbc.Error as e:
            print(f"[DB] fetch_procedure({proc}): {e}")
            raise
        finally:
            cur.close()

    def execute_procedure(self, proc: str, params: list = None) -> bool:
        """EXEC proc — không trả dữ liệu, commit."""
        conn = self._conn()
        cur = conn.cursor()
        try:
            if params:
                ph = ", ".join(["?"] * len(params))
                cur.execute(f"SET NOCOUNT ON; EXEC {proc} {ph}", params)
            else:
                cur.execute(f"SET NOCOUNT ON; EXEC {proc}")
            conn.commit()
            return True
        except pyodbc.Error as e:
            conn.rollback()
            print(f"[DB] execute_procedure({proc}): {e}")
            raise
        finally:
            cur.close()

    def execute_procedure_with_result(self, proc: str, params: list = None) -> list[dict]:
        """EXEC proc rồi đọc kết quả trả về (nếu có), sau đó commit."""
        conn = self._conn()
        cur = conn.cursor()
        try:
            if params:
                ph = ", ".join(["?"] * len(params))
                cur.execute(f"SET NOCOUNT ON; EXEC {proc} {ph}", params)
            else:
                cur.execute(f"SET NOCOUNT ON; EXEC {proc}")
            result = self._rows_to_dicts(cur)
            conn.commit()
            return result
        except pyodbc.Error as e:
            conn.rollback()
            print(f"[DB] execute_procedure_with_result({proc}): {e}")
            raise
        finally:
            cur.close()
