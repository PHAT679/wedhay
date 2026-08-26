# file: services/customer_service.py
import re
from repositories.customer_repository import CustomerRepository
from .base_service import BaseService

class CustomerService(BaseService):
    def __init__(self):
        self.repo = CustomerRepository()

    def get_customers(self) -> dict:
        raw_customers = self.repo.get_customers()
        raw_points    = self.repo.get_points()

        # Map points for O(1) lookup
        point_map = {}
        for p in raw_points:
            makh = self.pick(p, ["MAKH", "MA_KH"], "")
            if makh:
                point_map[makh] = self.pick(p, ["TONG_DIEM", "DIEM", "TONGDIEM"], 0)

        normalized_customers = []
        for row in raw_customers:
            makh = self.pick(row, ["MAKH", "MA_KH"], "N/A")
            normalized_customers.append({
                "MAKH": makh,
                "TENKH": self.pick(row, ["TENKH", "TEN_KH"], "N/A"),
                "SDT": self.pick(row, ["SDT", "SO_DIEN_THOAI"], ""),
                "DIACHI": self.pick(row, ["DIACHI", "DIA_CHI"], ""),
                "TONG_DIEM": point_map.get(makh, 0)
            })

        return {"success": True, "data": {
            "customers": normalized_customers,
            "customer_points": raw_points,
            "next_customer_id": self.repo.get_next_customer_id(),
        }}

    def get_customer_point_history(self, makh: str) -> dict:
        makh = (makh or "").strip()
        if not makh:
            return {"success": False, "message": "Thiếu mã khách hàng.", "data": []}
        try:
            rows = self.repo.get_customer_point_history(makh)
            return {"success": True, "data": rows}
        except Exception as e:
            print(f"[CustomerService] get_customer_point_history error: {e}")
            return {"success": False, "message": "Không thể lấy lịch sử điểm.", "data": []}

    def _validate_phone(self, sdt: str) -> bool:
        return bool(re.match(r'^0\d{9}$', sdt)) if sdt else True

    def add_customer(self, form: dict) -> dict:
        makh  = str(form.get("makh") or form.get("MAKH") or "").strip()
        tenkh = str(form.get("tenkh") or form.get("TENKH") or "").strip()
        sdt   = str(form.get("sdt") or form.get("dienthoai") or form.get("SDT") or "").strip()
        diachi = str(form.get("diachi") or form.get("DIACHI") or "").strip()

        if not makh:
            return {"success": False, "message": "Vui lòng nhập mã khách hàng."}
        if not tenkh:
            return {"success": False, "message": "Vui lòng nhập tên khách hàng."}
        if sdt and (not sdt.isdigit() or len(sdt) != 10 or not sdt.startswith("0")):
            return {"success": False, "message": "Số điện thoại không hợp lệ."}

        try:
            self.repo.add_customer(makh, tenkh, sdt or None, diachi or None)
            return {"success": True, "message": f"Thêm khách hàng {tenkh} thành công!"}
        except Exception as e:
            print(f"[CustomerService] add_customer error: {e}")
            err = str(e)
            if "CK_KH_SDT" in err:
                return {"success": False, "message": "Số điện thoại không đúng định dạng theo quy định hệ thống."}
            if "duplicate" in err.lower() or "trùng" in err.lower():
                return {"success": False, "message": "Mã khách hàng hoặc số điện thoại đã tồn tại."}
            return {"success": False, "message": "Thêm khách hàng thất bại."}

    def update_customer(self, makh: str, tenkh: str, sdt: str, diachi: str) -> dict:
        if not makh:
            return {"success": False, "message": "Thiếu mã khách hàng."}
        tenkh = (tenkh or "").strip()
        sdt   = (sdt or "").strip()
        if not tenkh:
            return {"success": False, "message": "Tên không được để trống."}
        if sdt and not self._validate_phone(sdt):
            return {"success": False, "message": "Số điện thoại không hợp lệ."}
        try:
            self.repo.update_customer(makh, tenkh, sdt or None, diachi or None)
            return {"success": True, "message": "Cập nhật khách hàng thành công!"}
        except Exception as e:
            print(f"[CustomerService] update_customer: {e}")
            return {"success": False, "message": "Cập nhật khách hàng thất bại."}
