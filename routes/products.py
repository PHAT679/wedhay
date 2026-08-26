"""
Products management routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from extensions import execute_query, execute_sp
from functools import wraps

products_bp = Blueprint('products', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@products_bp.route('/products')
@login_required
def index():
    try:
        products = execute_query("SELECT * FROM V_SANPHAM_BAN ORDER BY TENSANPHAM")
    except:
        try:
            products = execute_query("SELECT * FROM V_SANPHAM_TONKHO ORDER BY TENSANPHAM")
        except Exception as e:
            products = []
            flash(f'Không thể tải sản phẩm: {str(e)}', 'warning')
    
    return render_template('products.html', products=products)
