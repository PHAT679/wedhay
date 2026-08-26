// file: static/js/sales.js
// ── POS Sales Page ────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    initFilterCounts();
    setupSearch();
    setupCashCalculator();
    setupProductSelectButtons();
    setupCustomerPhoneLookup();

    // Prefill makh from customers page redirect
    const prefill = sessionStorage.getItem('prefill_makh');
    if (prefill) {
        const el = document.querySelector('input[name="makh"]');
        if (el) el.value = prefill;
        sessionStorage.removeItem('prefill_makh');
    }
});

function setupCustomerPhoneLookup() {
    const panel = document.getElementById('loyaltyPanel');
    const input = document.getElementById('customerPhoneInput');
    const hint = document.getElementById('customerLookupHint');
    if (!panel || !input || !hint || input.disabled) return;

    const customerByPhoneApi = panel.dataset.customerPhoneApi;
    const setCustomerApi = panel.dataset.setCustomerApi;
    let currentMakh = (panel.dataset.currentMakh || '').trim();
    let timer = null;

    const setHint = (text, type = 'muted') => {
        hint.textContent = text;
        hint.className = `customer-lookup-hint mb-2 ${type}`;
    };

    const setInvoiceCustomer = async (makh) => {
        const res = await fetch(setCustomerApi, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ makh: makh || '' }),
        });
        const data = await res.json();
        if (!res.ok || !data.success) {
            throw new Error(data.message || 'Không thể cập nhật khách hàng');
        }
        return data;
    };

    const lookup = async () => {
        const phone = (input.value || '').replace(/\D/g, '').slice(0, 10);
        input.value = phone;

        if (!phone) {
            setHint('Khách lẻ: không áp dụng tích điểm / sử dụng điểm.', 'muted');
            if (currentMakh) {
                await setInvoiceCustomer('');
                window.location.reload();
            }
            return;
        }

        if (phone.length < 10) {
            setHint('Nhập đủ 10 số để tự động tìm khách hàng.', 'muted');
            return;
        }

        setHint('Đang tìm khách hàng...', 'muted');
        const res = await fetch(`${customerByPhoneApi}?phone=${encodeURIComponent(phone)}`);
        const data = await res.json();

        if (res.ok && data.success && data.customer) {
            const foundMakh = (data.customer.MAKH || '').trim();
            setHint(`Đã nhận diện: ${foundMakh} - ${data.customer.TENKH || ''}`, 'success');
            if (foundMakh && foundMakh !== currentMakh) {
                await setInvoiceCustomer(foundMakh);
                window.location.reload();
            }
            return;
        }

        setHint('Khách lẻ / khách chưa có trong hệ thống.', 'muted');
        if (currentMakh) {
            await setInvoiceCustomer('');
            window.location.reload();
        }
    };

    if (input.value && input.value.length === 10) {
        setHint('Đã nhận diện khách hàng của hóa đơn hiện tại.', 'success');
    } else {
        setHint('Khách lẻ: không áp dụng tích điểm / sử dụng điểm.', 'muted');
    }

    input.addEventListener('input', () => {
        if (timer) clearTimeout(timer);
        timer = setTimeout(() => {
            lookup().catch((err) => {
                console.error(err);
                setHint('Không thể tìm khách lúc này.', 'danger');
            });
        }, 300);
    });
}

function setupProductSelectButtons() {
    const buttons = document.querySelectorAll('.btn-choose-product');
    buttons.forEach((btn) => {
        btn.addEventListener('click', () => {
            if (btn.classList.contains('disabled')) return;
            selectProduct(
                btn.dataset.maspct || '',
                btn.dataset.tensp || '',
                btn.dataset.mau || 'N/A',
                btn.dataset.size || 'N/A',
                btn.dataset.gia || 0
            );
        });
    });
}

// ── Product selection ─────────────────────────────────────────────
function selectProduct(maspct, tensp, mau = 'N/A', size = 'N/A', gia = 0) {
    const input = document.getElementById('maspctInput');
    if (input.disabled) {
        showToast('Vui lòng tạo hóa đơn trước!', 'danger');
        return;
    }

    input.value = maspct;
    
    const preview = document.getElementById('selectedProductPreview');
    if (preview) {
        preview.style.display = 'block';
        document.getElementById('selectedProductName').textContent = tensp || 'Sản phẩm';
        document.getElementById('selectedProductCode').textContent = `Mã: ${maspct || ''}`;
        document.getElementById('selectedProductVariant').textContent = `${mau || 'N/A'} / ${size || 'N/A'}`;
        const giaNum = Number(gia || 0);
        document.getElementById('selectedProductPrice').textContent = `Giá: ${new Intl.NumberFormat('vi-VN').format(giaNum)} đ`;
    }

    // Focus quantity
    const slInput = document.getElementById('soluongInput');
    if (slInput) { 
        slInput.value = 1;
        slInput.focus(); 
        slInput.select(); 
    }

    // Scroll to add item section smoothly
    document.getElementById('add-item-section').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function clearSelectedProduct() {
    document.getElementById('maspctInput').value = '';
    const preview = document.getElementById('selectedProductPreview');
    if (preview) preview.style.display = 'none';
}

// ── Qty controls ──────────────────────────────────────────────────
function changeQty(delta) {
    const input = document.getElementById('soluongInput');
    if (!input || input.disabled) return;
    let val = parseInt(input.value) + delta;
    input.value = Math.max(1, val);
}

// ── Generate invoice code ─────────────────────────────────────────
function generateInvoiceCode() {
    const el = document.getElementById('mahdCreate');
    if (!el || el.value) return;
    const now  = new Date();
    const code = 'HD' + now.getFullYear().toString().slice(-2) +
                 String(now.getMonth()+1).padStart(2,'0') +
                 String(now.getDate()).padStart(2,'0') +
                 String(now.getHours()).padStart(2,'0') +
                 String(now.getMinutes()).padStart(2,'0');
    el.value = code;
}

// ── Validate before submit ────────────────────────────────────────
function validateAddItem() {
    const sl = parseInt(document.getElementById('soluongInput')?.value);
    if (!sl || sl <= 0) {
        alert('Số lượng phải lớn hơn 0!');
        return false;
    }
    if (!document.getElementById('maspctInput')?.value) {
        alert('Vui lòng chọn sản phẩm từ danh sách bên phải!');
        return false;
    }
    return true;
}

// ── Cash Calculator ───────────────────────────────────────────────
function setupCashCalculator() {
    const inputTienKhach = document.getElementById('tienKhachDua');
    if (!inputTienKhach) return;

    inputTienKhach.addEventListener('input', calculateChange);
    // Initial calc if value exists
    if (inputTienKhach.value) calculateChange();
    
    // Calculate initial amount due as well
    calculateAmountDue();
}

function calculateAmountDue() {
    const tongTienHang = parseFloat(document.getElementById('tongTienHang')?.value || 0);
    const chietKhauPercent = parseFloat(document.getElementById('chietKhauPercent')?.value || 0);
    const usePointsCheck = document.getElementById('usePointsCheck');
    
    const tienChietKhau = tongTienHang * (chietKhauPercent / 100);
    let giamTuDiem = 0;
    
    if (usePointsCheck && usePointsCheck.checked) {
        giamTuDiem = 50000;
    }
    
    let khachCanTra = tongTienHang - tienChietKhau - giamTuDiem;
    if (khachCanTra < 0) khachCanTra = 0;
    
    // Update UI
    const elGiamDiem = document.getElementById('giamTuDiemDisplay');
    if (elGiamDiem) elGiamDiem.textContent = '- ' + new Intl.NumberFormat('vi-VN').format(giamTuDiem);
    
    const elTienChietKhau = document.getElementById('tienChietKhauDisplay');
    if (elTienChietKhau) elTienChietKhau.textContent = '- ' + new Intl.NumberFormat('vi-VN').format(tienChietKhau);
    
    const elKhachCanTra = document.getElementById('khachCanTraDisplay');
    if (elKhachCanTra) elKhachCanTra.textContent = new Intl.NumberFormat('vi-VN').format(khachCanTra);
    
    const inputTongCanThanhToan = document.getElementById('tongCanThanhToan');
    if (inputTongCanThanhToan) inputTongCanThanhToan.value = khachCanTra;
    
    calculateChange();
}

function calculateChange() {
    const tongTien = parseFloat(document.getElementById('tongCanThanhToan')?.value || 0);
    const tienKhach = parseFloat(document.getElementById('tienKhachDua')?.value || 0);
    
    const tienThuaEl = document.getElementById('tienThua');
    const msgEl = document.getElementById('paymentMessage');
    const btnThanhToan = document.getElementById('btnThanhToan');
    if (!tienThuaEl || !msgEl || !btnThanhToan) return;

    if (tienKhach <= 0 && tongTien > 0) {
        tienThuaEl.textContent = '0 đ';
        tienThuaEl.className = 'mb-0 fw-bold';
        msgEl.style.display = 'none';
        btnThanhToan.disabled = true;
        return;
    }

    const tienThua = tienKhach - tongTien;

    if (tienThua < 0) {
        tienThuaEl.textContent = '0 đ';
        tienThuaEl.className = 'mb-0 fw-bold';
        msgEl.style.display = 'block';
        btnThanhToan.disabled = true;
    } else {
        tienThuaEl.textContent = new Intl.NumberFormat('vi-VN').format(tienThua) + ' đ';
        tienThuaEl.className = 'mb-0 fw-bold text-success';
        msgEl.style.display = 'none';
        btnThanhToan.disabled = false;
    }
}

function setQuickCash(amount) {
    const el = document.getElementById('tienKhachDua');
    if (!el || el.disabled) return;
    el.value = amount;
    calculateChange();
}

function setExactCash() {
    const tongTien = document.getElementById('tongCanThanhToan')?.value || 0;
    const el = document.getElementById('tienKhachDua');
    if (!el || el.disabled) return;
    el.value = tongTien;
    calculateChange();
}

// ── Filter tabs ──────────────────────────────────────────────────
function filterProducts(btn, status) {
    document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const q    = (document.getElementById('posSearch')?.value || '').toLowerCase();
    const rows = document.querySelectorAll('#posTableBody tr.product-row');
    let visible = 0;
    rows.forEach(row => {
        const matchStatus = status === 'all' || row.dataset.status === status;
        const matchQ      = !q || row.textContent.toLowerCase().includes(q);
        const show = matchStatus && matchQ;
        row.style.display = show ? '' : 'none';
        if (show) visible++;
    });
}

// ── Search setup ──────────────────────────────────────────────────
function setupSearch() {
    const input = document.getElementById('posSearch');
    if (!input) return;

    input.addEventListener('input', () => {
        const activeTab = document.querySelector('.filter-tab.active');
        const status = activeTab?.dataset.filter || 'all';
        filterProducts(activeTab || document.querySelector('.filter-tab'), status);
    });
}

function clearSearch() {
    const input = document.getElementById('posSearch');
    if (input) input.value = '';
    const activeTab = document.querySelector('.filter-tab.active');
    filterProducts(activeTab || document.querySelector('.filter-tab'), activeTab?.dataset.filter || 'all');
}

// ── Count pills ───────────────────────────────────────────────────
function initFilterCounts() {
    const rows = document.querySelectorAll('#posTableBody tr.product-row');
    const counts = { all: rows.length, available: 0, low: 0, out: 0 };
    rows.forEach(r => {
        const s = r.dataset.status;
        if (counts[s] !== undefined) counts[s]++;
    });
}

// ── Toast helper ──────────────────────────────────────────────────
function showToast(msg, type = 'success') {
    const div = document.createElement('div');
    const bg = type === 'danger' ? '#dc3545' : '#0f172a';
    div.style.cssText = `position:fixed;top:80px;right:20px;z-index:9999;background:${bg};color:#fff;padding:10px 18px;border-radius:8px;font-size:13px;font-weight:600;box-shadow:0 4px 12px rgba(0,0,0,.3); transition: opacity 0.3s;`;
    div.innerHTML = type === 'danger' ? `<i class="bi bi-exclamation-circle-fill me-2"></i>${msg}` : `<i class="bi bi-check-circle-fill me-2"></i>${msg}`;
    document.body.appendChild(div);
    setTimeout(() => { div.style.opacity = '0'; setTimeout(() => div.remove(), 300); }, 2500);
}
