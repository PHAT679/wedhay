"""
Reports routes
"""

from flask import Blueprint, render_template, session, redirect, url_for, flash
from extensions import execute_query, execute_sp
from functools import wraps

reports_bp = Blueprint('reports', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@reports_bp.route('/reports')
@login_required
def index():
    data = {}
    
    try:
        data['doanh_thu'] = execute_query("SELECT * FROM V_DOANH_THU_THEO_THANG ORDER BY NAM DESC, THANG DESC")
    except:
        data['doanh_thu'] = []
    
    try:
        data['top_sp'] = execute_sp('usp_TOP_SANPHAM', fetch=True) or []
    except:
        data['top_sp'] = []
    
    try:
        data['nhanvien_ds'] = execute_query("SELECT * FROM V_NHANVIEN_DOANH_SO ORDER BY DOANHTHU DESC")
    except:
        data['nhanvien_ds'] = []
    
    try:
        data['cong_no'] = execute_query("SELECT * FROM V_CONG_NO_NHA_CUNG_CAP")
    except:
        data['cong_no'] = []
    
    try:
        data['ton_lau'] = execute_query("SELECT * FROM V_HANG_TON_LAU")
    except:
        data['ton_lau'] = []
    
    try:
        data['kh_nhieu_nhat'] = execute_query("SELECT TOP 10 * FROM V_KHACHHANG_MUANHIEUNHAT")
    except:
        data['kh_nhieu_nhat'] = []
    
    return render_template('reports.html', **data)
