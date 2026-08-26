"""
Authentication routes: login, logout
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from extensions import execute_query
import hashlib

auth_bp = Blueprint('auth', __name__)


def hash_password(password):
    """Hash password with MD5 (update to bcrypt for production)"""
    return hashlib.md5(password.encode()).hexdigest()


@auth_bp.route('/')
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Vui lòng nhập đầy đủ thông tin.', 'danger')
            return render_template('login.html')
        
        try:
            # Query user from NHANVIEN table - adjust column names to match your schema
            sql = """
                SELECT MANV, TENNV, ROLE, MATKHAU 
                FROM NHANVIEN 
                WHERE TENDANGNHAP = ? AND TRANGTHAI = 1
            """
            results = execute_query(sql, [username])
            
            if results:
                user = results[0]
                # Compare password (plain text - update to hash in production)
                stored_pw = user.get('MATKHAU', '')
                if stored_pw == password or stored_pw == hash_password(password):
                    session['user_id'] = user['MANV']
                    session['username'] = username
                    session['fullname'] = user.get('TENNV', username)
                    session['role'] = user.get('ROLE', 'seller').lower()
                    flash(f'Chào mừng {user.get("TENNV", username)}!', 'success')
                    return redirect(url_for('dashboard.index'))
                else:
                    flash('Mật khẩu không đúng.', 'danger')
            else:
                flash('Tài khoản không tồn tại hoặc đã bị vô hiệu hóa.', 'danger')
        except Exception as e:
            flash(f'Lỗi kết nối cơ sở dữ liệu: {str(e)}', 'danger')
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Bạn đã đăng xuất thành công.', 'info')
    return redirect(url_for('auth.login'))
