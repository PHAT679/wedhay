# file: services/purchase_service.py
from repositories.purchase_repository import PurchaseRepository
from .base_service import BaseService


class PurchaseService(BaseService):
    def __init__(self):
        self.repo = PurchaseRepository()

    def get_purchase_page_data(self, current_purchase_invoice_id=None) -> dict:
        items = []
        products = []
        suppliers = []
        summary = {
            "tong_so_luong": 0,
            "tong_tien_hang": 0,
            "chietkhau_percent": 0,
            "tien_chiet_khau": 0,
            "can_thanh_toan": 0
        }

        raw_products = self.repo.get_products_for_purchase()
        for p in raw_products:
            products.append({
                "MASPCT": self.pick(p, ["MASPCT", "MA_SPCT"], ""),
                "TENSP": self.pick(p, ["TENSP", "TENSANPHAM"], "N/A"),
                "MAU": self.pick(p, ["TEN_MAU", "MAU"], "N/A"),
                "SIZE": self.pick(p, ["TEN_SIZE", "SIZE"], "N/A"),
                "TONKHO": self.pick(p, ["SL_TONKHO", "TONKHO", "SOLUONG"], 0),
                "DONGIA_NHAP": self.pick(p, ["DONGIA_NHAP", "GIA_NHAP"], 0),
                "TRANG_THAI": self.pick(p, ["TRANG_THAI"], ""),
            })

        raw_suppliers = self.repo.get_suppliers()
        for s in raw_suppliers:
            suppliers.append({
                "MA_NCC": self.pick(s, ["MA_NCC", "ma_ncc", "MANCC"], ""),
                "TENNCC": self.pick(s, ["TENNCC", "tenncc", "TEN_NCC"], "Nhà cung cấp"),
                "DIACHI_NCC": self.pick(s, ["DIACHI_NCC", "diachi_ncc"], ""),
                "SDT_NCC": self.pick(s, ["SDT_NCC", "sdt_ncc"], ""),
                "STK_NCC": self.pick(s, ["STK_NCC", "stk_ncc"], ""),
            })

        if current_purchase_invoice_id:
            current_purchase = self.repo.get_purchase_invoice_info(current_purchase_invoice_id)
            raw_items = self.repo.get_purchase_items(current_purchase_invoice_id)
            for r in raw_items:
                items.append({
                    "MASPCT": self.pick(r, ["MASPCT", "MA_SPCT"], "N/A"),
                    "TENSP": self.pick(r, ["TENSP", "TENSANPHAM"], "N/A"),
                    "MAU": self.pick(r, ["TEN_MAU", "MAU"], "—"),
                    "SIZE": self.pick(r, ["TEN_SIZE", "SIZE"], "—"),
                    "SOLUONG_NHAP": self.pick(r, ["SOLUONG_NHAP"], 0),
                    "DONGIA_NHAP": self.pick(r, ["DONGIA_NHAP"], 0),
                    "THANH_TIEN": self.pick(r, ["THANH_TIEN"], 0)
                })
            raw_summary = self.repo.get_purchase_summary(current_purchase_invoice_id) or {}
            summary = {
                "tong_so_luong": raw_summary.get("tong_soluong") or raw_summary.get("TONG_SOLUONG") or 0,
                "tong_tien_hang": raw_summary.get("tong_tien_hang") or raw_summary.get("TONG_TIEN_HANG") or 0,
                "chietkhau_percent": raw_summary.get("chietkhau_percent") or raw_summary.get("CHIETKHAU_PERCENT") or 0,
                "tien_chiet_khau": raw_summary.get("tien_chiet_khau") or raw_summary.get("TIEN_CHIET_KHAU") or 0,
                "can_thanh_toan": raw_summary.get("can_thanh_toan") or raw_summary.get("CAN_THANH_TOAN") or 0,
            }

        next_id = self.repo.get_next_purchase_invoice_id() if not current_purchase_invoice_id else None

        return {
            "success": True,
            "next_purchase_invoice_id": next_id,
            "current_purchase_invoice_id": current_purchase_invoice_id,
            "current_purchase": current_purchase if 'current_purchase' in locals() else {},
            "purchase_items": items,
            "purchase_summary": summary,
            "products": products,
            "suppliers": suppliers,
        }

    def create_purchase_invoice(self, form_data: dict, session_user: dict) -> dict:
        mahdn = form_data.get("MAHDN", "").strip()
        mancc = form_data.get("MA_NCC", "").strip()
        manv = session_user.get("manv") or session_user.get("ma_nv", "") if session_user else ""

        if not mahdn or not mancc:
            return {"success": False, "message": "Mã phiếu nhập và mã nhà cung cấp không được để trống."}
        try:
            self.repo.create_purchase(mahdn, mancc, manv)
            return {"success": True, "message": f"Tạo phiếu nhập {mahdn} thành công!", "mahdn": mahdn}
        except Exception as e:
            msg = str(e)
            print(f"[PurchaseService] create_purchase_invoice: {e}")
            if "SQL Server" in msg and "]" in msg:
                parts = msg.split("]")
                for p in parts:
                    lower_p = p.lower()
                    if "tồn tại" in lower_p or "không tồn tại" in lower_p or "procedure expects parameter" in lower_p or "too many arguments" in lower_p or "cannot insert null" in lower_p:
                        msg = p.split("[SQL Server]")[-1].strip()
                        break
            return {"success": False, "message": msg}

    def add_purchase_item(self, mahdn: str, maspct: str, soluong: int) -> dict:
        try:
            self.repo.add_item(mahdn, maspct, soluong)
            return {"success": True, "message": f"Thêm sản phẩm {maspct} vào phiếu nhập thành công."}
        except Exception as e:
            msg = str(e)
            print(f"[PurchaseService] add_purchase_item error: {e}")
            if "SQL Server" in msg and "]" in msg:
                parts = msg.split("]")
                for p in parts:
                    lower_p = p.lower()
                    if "số lượng" in lower_p or "hóa đơn" in lower_p or "sản phẩm" in lower_p or "violation of primary key constraint" in lower_p or "tồn tại" in lower_p:
                        msg = p.split("[SQL Server]")[-1].strip()
                        break
            return {"success": False, "message": msg}

    def complete_purchase(self, mahdn: str) -> dict:
        if not mahdn:
            return {"success": False, "message": "Chưa có phiếu nhập để hoàn thành."}

        exists = self.repo.purchase_exists(mahdn)
        if not exists:
            return {"success": False, "message": "Phiếu nhập không tồn tại."}

        detail_count = self.repo.count_purchase_details(mahdn)
        if detail_count <= 0:
            return {"success": False, "message": "Phiếu nhập chưa có sản phẩm."}

        return {"success": True, "message": "Hoàn thành phiếu nhập thành công."}

    def update_purchase_discount(self, mahdn: str, chietkhau_raw) -> dict:
        if not mahdn:
            return {"success": False, "message": "Không xác định được mã phiếu nhập."}

        try:
            chietkhau = float(chietkhau_raw if chietkhau_raw is not None else 0)
        except (TypeError, ValueError):
            return {"success": False, "message": "Chiết khấu không hợp lệ."}

        if chietkhau < 0:
            chietkhau = 0
        if chietkhau > 100:
            chietkhau = 100

        exists = self.repo.purchase_exists(mahdn)
        if not exists:
            return {"success": False, "message": "Phiếu nhập không tồn tại."}

        self.repo.update_purchase_discount(mahdn, chietkhau)
        raw_summary = self.repo.get_purchase_summary(mahdn) or {}
        purchase_summary = {
            "tong_so_luong": raw_summary.get("tong_soluong") or raw_summary.get("TONG_SOLUONG") or 0,
            "tong_tien_hang": raw_summary.get("tong_tien_hang") or raw_summary.get("TONG_TIEN_HANG") or 0,
            "chietkhau_percent": raw_summary.get("chietkhau_percent") or raw_summary.get("CHIETKHAU_PERCENT") or 0,
            "tien_chiet_khau": raw_summary.get("tien_chiet_khau") or raw_summary.get("TIEN_CHIET_KHAU") or 0,
            "can_thanh_toan": raw_summary.get("can_thanh_toan") or raw_summary.get("CAN_THANH_TOAN") or 0,
        }
        return {"success": True, "purchase_summary": purchase_summary}
