# file: repositories/product_repository.py
from .base_repository import BaseRepository


class ProductRepository(BaseRepository):

    def get_products(self) -> list[dict]:
        return self.fetch_view("V_SANPHAM_BAN")

    def get_current_prices(self) -> list[dict]:
        return self.fetch_view("V_GIA_HIEN_TAI")

    def get_stock(self) -> list[dict]:
        return self.fetch_view("V_SANPHAM_TONKHO")

    def search_products(self, keyword=None, status="all") -> list[dict]:
        return self.fetch_procedure("dbo.usp_TIMKIEM_SANPHAM", [keyword, status])

    # ID generators
    def generate_product_id(self) -> str:
        res = self.fetch_procedure("dbo.usp_SINH_MA_SANPHAM")
        return res[0].get("MASP") if res else None

    def generate_product_detail_id(self) -> str:
        res = self.fetch_procedure("dbo.usp_SINH_MA_SANPHAM_CHITIET")
        return res[0].get("MASPCT") if res else None

    def add_product(self, maspct: str, tensp: str, ten_mau: str, ten_size: str, tenloaisp: str, dongia_ban: float, dongia_nhap: float):
        self.execute_procedure("dbo.usp_THEM_SANPHAM", [maspct, tensp, ten_mau, ten_size, tenloaisp, dongia_ban, dongia_nhap])

    def generate_category_id(self) -> str:
        res = self.fetch_procedure("dbo.usp_SINH_MA_LOAI_SANPHAM")
        return res[0].get("MALOAISP") if res else None

    def generate_color_id(self) -> str:
        res = self.fetch_procedure("dbo.usp_SINH_MA_MAU")
        return res[0].get("MA_MAU") if res else None

    def generate_size_id(self) -> str:
        res = self.fetch_procedure("dbo.usp_SINH_MA_SIZE")
        return res[0].get("MA_SIZE") if res else None

    def generate_price_id(self) -> str:
        res = self.fetch_procedure("dbo.usp_SINH_MA_BANGGIA")
        return res[0].get("MAGIA") if res else None

    # Finders
    def find_category_by_name(self, ten_loai: str) -> str:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT MALOAISP FROM LOAI_SANPHAM WHERE TEN_LOAI = ?", [ten_loai])
        row = cur.fetchone()
        return row[0] if row else None

    def find_product_by_name(self, tensp: str, maloaisp: str) -> str:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT MASP FROM SANPHAM WHERE TENSP = ? AND MALOAISP = ?", [tensp, maloaisp])
        row = cur.fetchone()
        return row[0] if row else None

    def find_color_by_name(self, ten_mau: str) -> str:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT MA_MAU FROM DANHMUC_MAU WHERE TEN_MAU = ?", [ten_mau])
        row = cur.fetchone()
        return row[0] if row else None

    def find_size_by_name(self, ten_size: str) -> str:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT MA_SIZE FROM DANHMUC_SIZE WHERE TEN_SIZE = ?", [ten_size])
        row = cur.fetchone()
        return row[0] if row else None

    def find_product_detail(self, masp: str, ma_mau: str, ma_size: str) -> str:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT MASPCT FROM SANPHAM_CHITIET WHERE MASP = ? AND MA_MAU = ? AND MA_SIZE = ?", [masp, ma_mau, ma_size])
        row = cur.fetchone()
        return row[0] if row else None

    # Inserters
    def insert_category(self, maloaisp: str, ten_loai: str):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO LOAI_SANPHAM (MALOAISP, TEN_LOAI) VALUES (?, ?)", [maloaisp, ten_loai])
        conn.commit()

    def insert_product(self, masp: str, tensp: str, maloaisp: str):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO SANPHAM (MASP, TENSP, MALOAISP) VALUES (?, ?, ?)", [masp, tensp, maloaisp])
        conn.commit()

    def insert_color(self, ma_mau: str, ten_mau: str):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO DANHMUC_MAU (MA_MAU, TEN_MAU) VALUES (?, ?)", [ma_mau, ten_mau])
        conn.commit()

    def insert_size(self, ma_size: str, ten_size: str):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO DANHMUC_SIZE (MA_SIZE, TEN_SIZE) VALUES (?, ?)", [ma_size, ten_size])
        conn.commit()

    def insert_product_detail(self, maspct: str, masp: str, ma_mau: str, ma_size: str, sl_tonkho: int):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO SANPHAM_CHITIET (MASPCT, MASP, MA_MAU, MA_SIZE, SL_TONKHO) VALUES (?, ?, ?, ?, ?)", [maspct, masp, ma_mau, ma_size, sl_tonkho])
        conn.commit()

    def insert_price(self, magia: str, maspct: str, dongia_ban: float, dongia_nhap: float):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO BANGGIA (MAGIA, MASPCT, DONGIA_BAN, DONGIA_NHAP, NGAY_BAT_DAU, NGAY_KET_THUC) VALUES (?, ?, ?, ?, GETDATE(), NULL)", [magia, maspct, dongia_ban, dongia_nhap])
        conn.commit()
