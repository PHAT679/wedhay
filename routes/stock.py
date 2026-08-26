"""
Inventory / Stock routes
"""

from flask import Blueprint, render_template, session, redirect, url_for, flash
from extensions import execute_query
from functools import wraps

stock_bp = Blueprint('stock', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@stock_bp.route('/stock')
@login_required
def index():
    data = {}
    try:
        data['tonkho'] = execute_query("SELECT * FROM V_SANPHAM_TONKHO ORDER BY TENSANPHAM")
    except Exception as e:
        data['tonkho'] = []
        flash(f'Lỗi tải tồn kho: {str(e)}', 'warning')
    
    try:
        data['sap_het'] = execute_query("SELECT * FROM V_SANPHAM_SAP_HET ORDER BY SOLUONG")
    except:
        data['sap_het'] = []
    
    try:
        data['ton_lau'] = execute_query("SELECT * FROM V_HANG_TON_LAU")
    except:
        data['ton_lau'] = []
    
    return render_template('stock.html', **data)
