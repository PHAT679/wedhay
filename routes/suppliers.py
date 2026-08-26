"""
Suppliers routes
"""

from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from extensions import execute_query, execute_sp
from functools import wraps

suppliers_bp = Blueprint('suppliers', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@suppliers_bp.route('/suppliers')
@login_required
def index():
    data = {}
    try:
        data['suppliers'] = execute_query("SELECT * FROM NHACUNGCAP ORDER BY TENNCC")
    except Exception as e:
        data['suppliers'] = []
        flash(f'Không thể tải nhà cung cấp: {str(e)}', 'warning')
    
    try:
        data['cong_no'] = execute_query("SELECT * FROM V_CONG_NO_NHA_CUNG_CAP")
    except:
        try:
            data['cong_no'] = execute_query("SELECT * FROM V_CONGNO_HOADON")
        except:
            data['cong_no'] = []
    
    return render_template('suppliers.html', **data)


@suppliers_bp.route('/suppliers/add', methods=['POST'])
@login_required
def add_supplier():
    mancc = request.form.get('mancc', '').strip()
    tenncc = request.form.get('tenncc', '').strip()
    dienthoai = request.form.get('dienthoai', '').strip()
    diachi = request.form.get('diachi', '').strip()
    
    if not tenncc:
        flash('Tên nhà cung cấp không được để trống.', 'danger')
        return redirect(url_for('suppliers.index'))
    
    try:
        execute_query(
            "INSERT INTO NHACUNGCAP (MANCC, TENNCC, DIENTHOAI, DIACHI) VALUES (?, ?, ?, ?)",
            [mancc, tenncc, dienthoai or None, diachi or None],
            fetch=False
        )
        flash(f'Thêm nhà cung cấp {tenncc} thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi thêm nhà cung cấp: {str(e)}', 'danger')
    
    return redirect(url_for('suppliers.index'))
