# file: services/product_service.py
from repositories.product_repository import ProductRepository
from .base_service import BaseService

class ProductService(BaseService):
    def __init__(self):
        self.repo = ProductRepository()

    def get_products(self) -> dict:
        raw_products = self.repo.get_products()
        normalized = []
        for row in raw_products:
            # Dùng helper pick để map đúng cột từ database thật
            maspct = self.pick(row, ["MASPCT", "MA_SPCT"], "")
            tensp = self.pick(row, ["TENSP", "TENSANPHAM", "TEN_SANPHAM"], "N/A")
            loai = self.pick(row, ["LOAI", "TENLOAI", "TEN_LOAI", "LOAISANPHAM"], "")
            mau = self.pick(row, ["TEN_MAU", "MAU", "TENMAU"], "")
            size = self.pick(row, ["TEN_SIZE", "SIZE", "COKISIZE", "TENSIZE"], "")
            gia_ban = self.pick(row, ["DONGIA_BAN", "GIABAN", "GIA_BAN"], 0)
            gia_nhap = self.pick(row, ["DONGIA_NHAP", "GIANHAP", "GIA_NHAP"], 0)
            ton_kho = self.pick(row, ["SL_TONKHO", "SOLUONG", "TONKHO", "TON_KHO"], 0)

            normalized.append({
                "MASPCT": maspct,
                "TENSANPHAM": tensp,
                "LOAISANPHAM": loai,
                "MAU": mau,
                "SIZE": size,
                "GIABAN": gia_ban,
                "GIANHAP": gia_nhap,
                "TONKHO": ton_kho
            })
        return {"success": True, "data": normalized}

    def get_products_page_data(self, keyword=None, status="all") -> dict:
        try:
            raw_products = self.repo.search_products(keyword, status)
            if raw_products is None:
                return {"success": False, "message": "Lỗi khi gọi procedure tìm kiếm.", "data": {"products": []}}
            
            normalized = []
            for row in raw_products:
                ton_kho = self.pick(row, ["SL_TONKHO"], 0)
                
                # Determine state properly, assuming TRANG_THAI gives a hint if not empty, but we can fall back to stock level
                if ton_kho <= 0:
                    trang_thai = "Hết hàng"
                elif ton_kho <= 5:
                    trang_thai = "Sắp hết"
                else:
                    trang_thai = "Còn hàng"
                
                normalized.append({
                    "ma_spct": self.pick(row, ["MASPCT"], ""),
                    "ma_sp": self.pick(row, ["MASP"], ""),
                    "ten_san_pham": self.pick(row, ["TENSP"], "N/A"),
                    "loai": "—", # Because procedure doesn't return LOAISANPHAM
                    "mau": self.pick(row, ["TEN_MAU"], ""),
                    "size": self.pick(row, ["TEN_SIZE"], ""),
                    "gia_ban": self.pick(row, ["DONGIA_BAN"], 0),
                    "gia_nhap": self.pick(row, ["DONGIA_NHAP"], 0),
                    "ton_kho": ton_kho,
                    "trang_thai": self.pick(row, ["TRANG_THAI"], trang_thai)
                })
            return {"success": True, "data": {"products": normalized}}
        except Exception as e:
            print(f"[ProductService] get_products_page_data: {e}")
            return {"success": False, "message": "Lỗi trong quá trình tìm kiếm.", "data": {"products": []}}

    def get_next_product_detail_id(self) -> str:
        try:
            return self.repo.generate_product_detail_id() or "Không thể sinh mã SP chi tiết"
        except Exception as e:
            print(f"[ProductService] get_next_product_detail_id error: {e}")
            return "Không thể sinh mã SP chi tiết"

    def create_product(self, form_data: dict) -> dict:
        maspct = form_data.get("MASPCT", "").strip()
        tensp = form_data.get("TENSP", "").strip()
        ten_mau = form_data.get("TEN_MAU", "").strip()
        ten_size = form_data.get("TEN_SIZE", "").strip()
        tenloaisp = form_data.get("TENLOAISP", "").strip()
        
        try:
            dongia_ban = float(form_data.get("DONGIA_BAN", 0))
            dongia_nhap = float(form_data.get("DONGIA_NHAP", 0))
        except ValueError:
            return {"success": False, "message": "Giá bán và giá nhập phải là số."}

        if not maspct: return {"success": False, "message": "Mã sản phẩm chi tiết không được để trống."}
        if not tensp: return {"success": False, "message": "Tên sản phẩm không được để trống."}
        if not ten_mau: return {"success": False, "message": "Màu sắc không được để trống."}
        if not ten_size: return {"success": False, "message": "Size không được để trống."}
        if not tenloaisp: return {"success": False, "message": "Loại sản phẩm không được để trống."}
        if dongia_ban < 0: return {"success": False, "message": "Giá bán không hợp lệ."}
        if dongia_nhap < 0: return {"success": False, "message": "Giá nhập không hợp lệ."}

        try:
            self.repo.add_product(maspct, tensp, ten_mau, ten_size, tenloaisp, dongia_ban, dongia_nhap)
            return {"success": True, "message": f"Thêm sản phẩm '{tensp}' thành công!"}

        except Exception as e:
            msg = str(e)
            print(f"[ProductService] create_product error: {e}")
            if "SQL Server" in msg and "]" in msg:
                parts = msg.split("]")
                for p in parts:
                    lower_p = p.lower()
                    if "tồn tại" in lower_p or "không hợp lệ" in lower_p or "chống trùng" in lower_p or "violation" in lower_p or "không được để trống" in lower_p:
                        msg = p.split("[SQL Server]")[-1].strip()
                        break
            return {"success": False, "message": msg}
