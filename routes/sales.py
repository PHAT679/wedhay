"""
Sales / POS routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from extensions import execute_query, execute_sp
from functools import wraps

sales_bp = Blueprint('sales', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@sales_bp.route('/sales')
@login_required
def index():
    try:
        products = execute_query("SELECT * FROM V_SANPHAM_BAN ORDER BY TENSANPHAM")
    except Exception as e:
        products = []
        flash(f'Không thể tải danh sách sản phẩm: {str(e)}', 'warning')
    
    return render_template('sales.html', products=products)


@sales_bp.route('/sales/create-invoice', methods=['POST'])
@login_required
def create_invoice():
    mahd = request.form.get('mahd', '').strip()
    makh = request.form.get('makh', '').strip()
    manv = request.form.get('manv', session.get('user_id', '')).strip()
    chiet_khau = request.form.get('chiet_khau', 0)
    
    if not mahd:
        flash('Vui lòng nhập mã hóa đơn.', 'danger')
        return redirect(url_for('sales.index'))
    
    try:
        chiet_khau = float(chiet_khau) if chiet_khau else 0
        execute_sp('usp_TAO_HOADON_BAN', [mahd, makh or None, manv, chiet_khau])
        flash(f'Tạo hóa đơn {mahd} thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi tạo hóa đơn: {str(e)}', 'danger')
    
    return redirect(url_for('sales.index'))


@sales_bp.route('/sales/add-item', methods=['POST'])
@login_required
def add_item():
    mahd = request.form.get('mahd', '').strip()
    maspct = request.form.get('maspct', '').strip()
    soluong = request.form.get('soluong', 0)
    
    if not mahd or not maspct:
        flash('Vui lòng nhập đủ mã hóa đơn và mã sản phẩm.', 'danger')
        return redirect(url_for('sales.index'))
    
    try:
        soluong = int(soluong)
        if soluong <= 0:
            flash('Số lượng phải lớn hơn 0.', 'danger')
            return redirect(url_for('sales.index'))
        
        # Kiểm tra tồn kho trước
        try:
            execute_sp('usp_KiemTraTonKho', [maspct, soluong])
        except Exception as ek:
            flash(f'Lỗi tồn kho: {str(ek)}', 'danger')
            return redirect(url_for('sales.index'))
        
        execute_sp('usp_THEM_CTHDB', [mahd, maspct, soluong])
        flash(f'Đã thêm sản phẩm {maspct} x{soluong} vào hóa đơn {mahd}.', 'success')
    except ValueError:
        flash('Số lượng không hợp lệ.', 'danger')
    except Exception as e:
        flash(f'Lỗi thêm sản phẩm: {str(e)}', 'danger')
    
    return redirect(url_for('sales.index'))


@sales_bp.route('/sales/checkout', methods=['POST'])
@login_required
def checkout():
    mahd = request.form.get('mahd', '').strip()
    tien_khach = request.form.get('tien_khach', 0)
    
    if not mahd:
        flash('Vui lòng nhập mã hóa đơn.', 'danger')
        return redirect(url_for('sales.index'))
    
    try:
        tien_khach = float(tien_khach)
        if tien_khach <= 0:
            flash('Tiền khách đưa phải lớn hơn 0.', 'danger')
            return redirect(url_for('sales.index'))
        
        execute_sp('usp_THANH_TOAN_HOADON_BAN', [mahd, tien_khach])
        flash(f'Thanh toán hóa đơn {mahd} thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi thanh toán: {str(e)}', 'danger')
    
    return redirect(url_for('sales.index'))


@sales_bp.route('/sales/search')
@login_required
def search_products():
    """AJAX endpoint to search products"""
    q = request.args.get('q', '').strip()
    try:
        if q:
            products = execute_query(
                "SELECT * FROM V_SANPHAM_BAN WHERE TENSANPHAM LIKE ? OR MASPCT LIKE ? ORDER BY TENSANPHAM",
                [f'%{q}%', f'%{q}%']
            )
        else:
            products = execute_query("SELECT * FROM V_SANPHAM_BAN ORDER BY TENSANPHAM")
        return jsonify(products)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
