"""
Dashboard routes
"""

from flask import Blueprint, render_template, session, redirect, url_for
from extensions import execute_query, execute_sp
from functools import wraps

dashboard_bp = Blueprint('dashboard', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@dashboard_bp.route('/dashboard')
@login_required
def index():
    data = {}
    
    try:
        # Doanh thu theo tháng
        data['doanh_thu'] = execute_query("SELECT * FROM V_DOANH_THU_THEO_THANG ORDER BY NAM DESC, THANG DESC")
    except:
        data['doanh_thu'] = []
    
    try:
        # Top sản phẩm bán chạy
        data['top_sp'] = execute_sp('usp_TOP_SANPHAM', fetch=True) or []
    except:
        data['top_sp'] = []
    
    try:
        # Tồn kho tổng
        data['tonkho'] = execute_query("SELECT COUNT(*) AS TONG FROM V_SANPHAM_TONKHO")
        data['tong_sp'] = data['tonkho'][0]['TONG'] if data['tonkho'] else 0
    except:
        data['tong_sp'] = 0
    
    try:
        # Sản phẩm sắp hết
        data['sap_het'] = execute_query("SELECT * FROM V_SANPHAM_SAP_HET")
        data['so_sap_het'] = len(data['sap_het'])
    except:
        data['sap_het'] = []
        data['so_sap_het'] = 0
    
    try:
        # Hàng tồn lâu
        data['ton_lau'] = execute_query("SELECT TOP 5 * FROM V_HANG_TON_LAU")
        data['so_ton_lau'] = len(execute_query("SELECT * FROM V_HANG_TON_LAU") or [])
    except:
        data['ton_lau'] = []
        data['so_ton_lau'] = 0
    
    try:
        # Doanh thu tháng này
        dt = execute_query("""
            SELECT TOP 1 DOANHTHU FROM V_DOANH_THU_THEO_THANG
            WHERE THANG = MONTH(GETDATE()) AND NAM = YEAR(GETDATE())
        """)
        data['doanh_thu_thang'] = dt[0]['DOANHTHU'] if dt else 0
    except:
        data['doanh_thu_thang'] = 0

    return render_template('dashboard.html', **data)
