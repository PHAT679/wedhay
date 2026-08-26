# file: repositories/customer_repository.py
from .base_repository import BaseRepository
import pyodbc


class CustomerRepository(BaseRepository):

    def get_customers(self) -> list[dict]:
        return self.fetch_view("V_KHACHHANG")

    def get_points(self) -> list[dict]:
        return self.fetch_view("V_DIEM_KHACHHANG")

    def add_customer(self, makh: str, tenkh: str, sdt: str, diachi: str):
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT p.name
                FROM sys.parameters p
                INNER JOIN sys.objects o ON p.object_id = o.object_id
                WHERE o.type = 'P' AND o.name = 'usp_THEM_KHACHHANG'
                ORDER BY p.parameter_id
                """
            )
            params = [str(row[0]).lstrip("@").upper() for row in cur.fetchall()]
            if not params:
                raise pyodbc.Error("Không tìm thấy tham số của procedure usp_THEM_KHACHHANG.")

            value_map = {
                "MAKH": makh,
                "MA_KH": makh,
                "TENKH": tenkh,
                "TEN_KH": tenkh,
                "HOTEN": tenkh,
                "SDT": sdt,
                "DIENTHOAI": sdt,
                "SO_DIEN_THOAI": sdt,
                "DIACHI": diachi,
                "DIACHI": diachi,
                "DIA_CHI": diachi,
            }
            exec_parts = []
            exec_values = []
            for p in params:
                value = value_map.get(p)
                exec_parts.append(f"@{p} = ?")
                exec_values.append(value)

            sql = "SET NOCOUNT ON; EXEC usp_THEM_KHACHHANG " + ", ".join(exec_parts)
            cur.execute(sql, exec_values)
            conn.commit()
        except pyodbc.Error:
            conn.rollback()
            raise
        finally:
            cur.close()

    def update_customer(self, makh: str, tenkh: str, sdt: str, diachi: str):
        self.execute_procedure("usp_CAPNHAT_KHACHHANG", [makh, tenkh, sdt, diachi])

    def get_next_customer_id(self):
        """Lấy mã khách hàng tiếp theo từ usp_SINH_MA_KHACHHANG"""
        try:
            result = self.fetch_procedure("usp_SINH_MA_KHACHHANG")
            if result and len(result) > 0:
                return result[0].get("MAKH")
        except Exception as e:
            print(f"[CustomerRepo] get_next_customer_id error: {e}")
        return None

    def get_customer_point_history(self, makh: str) -> list[dict]:
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT
                    ID,
                    MAKH,
                    MAHDB,
                    DIEM_THAYDOI,
                    CASE
                        WHEN DIEM_THAYDOI > 0 THEN N'Tích điểm'
                        WHEN DIEM_THAYDOI < 0 THEN N'Sử dụng điểm'
                        ELSE N'Không đổi'
                    END AS LOAI_DIEM
                FROM DIEMTICHLUY
                WHERE MAKH = ?
                ORDER BY ID DESC
                """,
                [makh]
            )
            return self._rows_to_dicts(cur)
        finally:
            cur.close()
