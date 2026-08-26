# file: services/auth_service.py
from repositories.auth_repository import AuthRepository
from .base_service import BaseService

def normalize_role(role_raw):
    role_text = str(role_raw or "").strip().lower()
    role_text_normalized = role_text.replace("_", " ").replace("-", " ")

    if role_text in {"admin", "admin_role", "administrator"} or "quản trị" in role_text or "quan tri" in role_text:
        return "admin"

    if (
        role_text in {"banhang", "ban_hang", "banhang_role", "seller", "seller_role", "sale", "sales", "cashier"}
        or role_text_normalized in {"ban hang", "thu ngan"}
        or "bán hàng" in role_text
        or "ban hang" in role_text_normalized
        or "thu ngân" in role_text
        or "thu ngan" in role_text_normalized
    ):
        return "banhang"

    if role_text in {"kho", "kho_role", "warehouse"} or "thủ kho" in role_text or "thu kho" in role_text_normalized:
        return "kho"

    return role_text

class AuthService(BaseService):
    def __init__(self):
        self.repo = AuthRepository()

    def login(self, username: str, password: str) -> dict:
        username = (username or "").strip()
        password = (password or "").strip()

        if not username or not password:
            return {"success": False, "message": "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu."}

        try:
            user = self.repo.login(username, password)
            try:
                print("LOGIN USER ROW:", str(user).encode("utf-8", "replace").decode("utf-8"))
            except Exception:
                pass
            
            if user is None:
                return {"success": False, "message": "Tên đăng nhập hoặc mật khẩu không đúng."}

            role_value = self.pick(user, ["role", "ROLE", "Role"], "")
            role_raw = self.pick(
                user,
                ["role_raw", "ROLE_RAW", "role_name", "ROLE_NAME", "VAITRO"],
                ""
            )
            mapped_role = normalize_role(role_value or role_raw)
            
            print("DEBUG LOGIN ROLE FIELD:", role_value)
            print("DEBUG LOGIN RAW ROLE:", role_raw)
            print("DEBUG NORMALIZED ROLE:", mapped_role)

            uname = self.pick(user, ["username", "USERNAME", "Username", "TENDANGNHAP"], username)
            fname = self.pick(user, ["full_name", "FULL_NAME", "Full_name", "HOTEN", "TENNV", "TEN_NV"], uname)
            manv = self.pick(user, ["manv", "MANV", "MA_NV"], "")
            if mapped_role not in {"admin", "banhang", "kho"}:
                return {"success": False, "message": "Tài khoản không có vai trò hợp lệ để đăng nhập hệ thống."}

            return {
                "success": True,
                "message": "Đăng nhập thành công.",
                "data": {
                    "username": uname,
                    "role": mapped_role,
                    "role_raw": role_raw or role_value,
                    "full_name": fname,
                    "manv": manv
                }
            }
        except Exception as e:
            print(f"[AuthService] login error: {e}")
            return {"success": False, "message": "Không thể kết nối hoặc xác thực tài khoản. Vui lòng kiểm tra database."}
