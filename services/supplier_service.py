# file: services/supplier_service.py
from repositories.supplier_repository import SupplierRepository
# import pyodbc


class SupplierService:
    def __init__(self):
        self.repo = SupplierRepository()

    def get_all_suppliers(self) -> list[dict]:
        return self.repo.get_all_suppliers()

    def get_supplier_debts(self) -> list[dict]:
        debts = self.repo.get_supplier_debts()
        return debts

    def get_unpaid_purchase_invoices(self, ma_ncc: str) -> list[dict]:
        ma_ncc = (ma_ncc or "").strip()
        if not ma_ncc:
            raise ValueError("Thiếu mã nhà cung cấp.")
        invoices = self.repo.get_unpaid_purchase_invoices(ma_ncc)

        normalized = []
        for inv in invoices:
            tongtien = float(inv.get("tongtien") or 0)
            chietkhau = float(inv.get("chietkhau") or 0)

            tien_chiet_khau = inv.get("tien_chiet_khau")
            if tien_chiet_khau is None:
                tien_chiet_khau = tongtien * chietkhau / 100
            tien_chiet_khau = float(tien_chiet_khau or 0)

            phai_tra = inv.get("phai_tra")
            if phai_tra is None:
                phai_tra = tongtien - tien_chiet_khau
            phai_tra = float(phai_tra or 0)
            if phai_tra < 0:
                phai_tra = 0

            da_tra = float(inv.get("da_tra") or 0)
            cong_no = inv.get("cong_no")
            if cong_no is None:
                cong_no = phai_tra - da_tra
            cong_no = float(cong_no or 0)
            if cong_no < 0:
                cong_no = 0

            normalized.append({
                **inv,
                "tongtien": tongtien,
                "chietkhau": chietkhau,
                "tien_chiet_khau": tien_chiet_khau,
                "phai_tra": phai_tra,
                "da_tra": da_tra,
                "cong_no": cong_no,
                "trang_thai": inv.get("trang_thai") or ("Đã thanh toán" if cong_no == 0 else "Còn nợ"),
            })

        return normalized

    def pay_supplier_debt(self, mahdn: str, sotientra_raw) -> dict:
        mahdn = (mahdn or "").strip()
        if not mahdn:
            return {"success": False, "message": "Thiếu mã hóa đơn nhập."}

        try:
            sotientra = float(sotientra_raw)
        except (TypeError, ValueError):
            return {"success": False, "message": "Số tiền thanh toán không hợp lệ."}

        if sotientra <= 0:
            return {"success": False, "message": "Số tiền thanh toán phải lớn hơn 0."}

        try:
            matt = self.repo.generate_payment_id()
            if not matt:
                return {"success": False, "message": "Không thể sinh mã thanh toán."}
            print("===== PAY SUPPLIER DEBT DEBUG =====")
            print("GENERATED MATT:", matt)
            print("MAHDN:", mahdn)
            print("SOTIENTRA:", sotientra)
            self.repo.pay_supplier_debt(matt, mahdn, sotientra)
            return {"success": True, "message": "Thanh toán công nợ thành công."}
        except Exception as e:
            msg = str(e)
            if "SQL Server" in msg and "]" in msg:
                parts = msg.split("]")
                for p in parts:
                    if "vượt quá số nợ" in p.lower() or "số tiền" in p.lower() or "không tồn tại" in p.lower():
                        msg = p.split("[SQL Server]")[-1].strip()
                        break
            print(f"[SupplierService] pay_supplier_debt error: {e}")
            return {"success": False, "message": msg}

    def get_current_database(self) -> str | None:
        return self.repo.get_current_database()

    def get_suppliers(self) -> dict:
        try:
            suppliers = self.get_all_suppliers()
            supplier_debts = self.get_supplier_debts()
            next_supplier_id = self.repo.get_next_supplier_id()
        except Exception as e:
            print(f"[SupplierService] get_suppliers error: {e}")
            return {
                "success": False,
                "message": f"Không thể tải dữ liệu nhà cung cấp từ SQL Server: {e}",
                "data": {
                    "suppliers": [],
                    "supplier_debts": [],
                    "next_supplier_id": None,
                    "current_db": None,
                }
            }

        return {
            "success": True,
            "data": {
                "suppliers": suppliers,
                "supplier_debts": supplier_debts,
                "next_supplier_id": next_supplier_id,
                "current_db": self.get_current_database(),
            }
        }

    def add_supplier(self, form: dict) -> dict:
        mancc  = str(form.get("mancc") or form.get("MANCC") or "").strip()
        tenncc = str(form.get("tenncc") or form.get("TENNCC") or "").strip()
        sdt_ncc = str(form.get("sdt_ncc") or form.get("dienthoai") or form.get("DIENTHOAI") or form.get("SDT_NCC") or form.get("sdt") or "").strip()
        diachi_ncc = str(form.get("diachi_ncc") or form.get("diachi") or form.get("DIACHI_NCC") or form.get("DIACHI") or "").strip()
        stk_ncc_raw = form.get("stk_ncc") or form.get("STK_NCC")

        if not tenncc:
            return {"success": False, "message": "Tên nhà cung cấp không được để trống."}
        if sdt_ncc and (not sdt_ncc.isdigit() or len(sdt_ncc) != 10 or not sdt_ncc.startswith("0")):
            return {"success": False, "message": "Số điện thoại nhà cung cấp phải gồm 10 số và bắt đầu bằng 0."}

        stk_ncc = str(stk_ncc_raw).strip() if stk_ncc_raw is not None else ""
        if stk_ncc and not stk_ncc.isdigit():
            return {"success": False, "message": "Số tài khoản chỉ được gồm chữ số."}

        sdt_ncc = sdt_ncc or None
        diachi_ncc = diachi_ncc or None
        stk_ncc = stk_ncc or None
        try:
            self.repo.add_supplier(mancc or "", tenncc, sdt_ncc, diachi_ncc, stk_ncc)
            return {"success": True, "message": f"Thêm nhà cung cấp {tenncc} thành công!"}
        except pyodbc.Error as e:
            print("ADD SUPPLIER SQL ERROR:", e)
            return {"success": False, "message": self._extract_sql_message(e)}
        except Exception as e:
            print(f"[SupplierService] add_supplier: {e}")
            return {"success": False, "message": "Thêm nhà cung cấp thất bại."}

    @staticmethod
    def _extract_sql_message(error: pyodbc.Error) -> str:
        raw_message = str(error)
        if "[SQL Server]" in raw_message:
            sql_message = raw_message.split("[SQL Server]")[-1].strip()
            if sql_message:
                return sql_message
        return raw_message

    def update_supplier(self, mancc: str, tenncc: str, dienthoai: str, diachi: str) -> dict:
        if not mancc:
            return {"success": False, "message": "Thiếu mã nhà cung cấp."}
        try:
            self.repo.update_supplier(mancc, tenncc or "", dienthoai or "", diachi or "")
            return {"success": True, "message": "Cập nhật nhà cung cấp thành công!"}
        except Exception as e:
            print(f"[SupplierService] update_supplier: {e}")
            return {"success": False, "message": "Cập nhật nhà cung cấp thất bại."}
