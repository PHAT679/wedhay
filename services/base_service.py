# file: services/base_service.py
class BaseService:
    @staticmethod
    def pick(row, keys, default=None):
        """Helper để lấy giá trị linh hoạt từ dict dựa trên danh sách các keys."""
        if not row:
            return default
        for key in keys:
            if key in row and row[key] is not None:
                return row[key]
        return default
