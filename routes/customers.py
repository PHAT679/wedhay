"""
Customers routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from extensions import execute_query, execute_sp
from functools import wraps
import re

customers_bp = Blueprint('customers', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@customers_bp.route('/customers')
@login_required
def index():
    try:
        customers = execute_query("SELECT * FROM V_KHACHHANG ORDER BY TENKHACHHANG")
    except:
        try:
            customers = execute_query("SELECT * FROM KHACHHANG ORDER BY TENKHACHHANG")
        except Exception as e:
            customers = []
            flash(f'Không thể tải danh sách khách hàng: {str(e)}', 'warning')
    
    return render_template('customers.html', customers=customers)


@customers_bp.route('/customers/add', methods=['POST'])
@login_required
def add_customer():
    makh = request.form.get('makh', '').strip()
    tenkh = request.form.get('tenkh', '').strip()
    dienthoai = request.form.get('dienthoai', '').strip()
    diachi = request.form.get('diachi', '').strip()
    
    # Validate
    if not tenkh:
        flash('Tên khách hàng không được để trống.', 'danger')
        return redirect(url_for('customers.index'))
    
    if dienthoai:
        if not re.match(r'^0\d{9}$', dienthoai):
            flash('Số điện thoại phải gồm 10 số và bắt đầu bằng 0.', 'danger')
            return redirect(url_for('customers.index'))
    
    try:
        execute_sp('usp_THEM_KHACHHANG', [makh, tenkh, dienthoai or None, diachi or None])
        flash(f'Thêm khách hàng {tenkh} thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi thêm khách hàng: {str(e)}', 'danger')
    
    return redirect(url_for('customers.index'))
