"""
Purchase / Import routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from extensions import execute_query, execute_sp
from functools import wraps

purchase_bp = Blueprint('purchase', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@purchase_bp.route('/purchase')
@login_required
def index():
    data = {}
    try:
        data['phieu_nhap'] = execute_query("""
            SELECT TOP 50 * FROM HOADON_NHAP 
            ORDER BY NGAYNHAP DESC
        """)
    except:
        try:
            data['phieu_nhap'] = execute_query("SELECT TOP 50 * FROM V_PHIEU_NHAP ORDER BY NGAYNHAP DESC")
        except Exception as e:
            data['phieu_nhap'] = []
            flash(f'Không thể tải phiếu nhập: {str(e)}', 'warning')
    return render_template('purchase.html', **data)


@purchase_bp.route('/purchase/create', methods=['POST'])
@login_required
def create_purchase():
    mahdn = request.form.get('mahdn', '').strip()
    mancc = request.form.get('mancc', '').strip()
    manv = request.form.get('manv', session.get('user_id', '')).strip()
    
    if not mahdn or not mancc:
        flash('Vui lòng nhập đầy đủ mã phiếu nhập và nhà cung cấp.', 'danger')
        return redirect(url_for('purchase.index'))
    
    try:
        execute_sp('usp_TAO_HOADON_NHAP', [mahdn, mancc, manv])
        flash(f'Tạo phiếu nhập {mahdn} thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi tạo phiếu nhập: {str(e)}', 'danger')
    
    return redirect(url_for('purchase.index'))


@purchase_bp.route('/purchase/add-item', methods=['POST'])
@login_required
def add_item():
    mahdn = request.form.get('mahdn', '').strip()
    maspct = request.form.get('maspct', '').strip()
    soluong = request.form.get('soluong', 0)
    
    if not mahdn or not maspct:
        flash('Vui lòng nhập đủ thông tin.', 'danger')
        return redirect(url_for('purchase.index'))
    
    try:
        soluong = int(soluong)
        if soluong <= 0:
            flash('Số lượng phải lớn hơn 0.', 'danger')
            return redirect(url_for('purchase.index'))
        
        execute_sp('usp_THEM_CTHDN', [mahdn, maspct, soluong])
        flash(f'Đã thêm {maspct} x{soluong} vào phiếu nhập {mahdn}.', 'success')
    except Exception as e:
        flash(f'Lỗi thêm sản phẩm nhập: {str(e)}', 'danger')
    
    return redirect(url_for('purchase.index'))
