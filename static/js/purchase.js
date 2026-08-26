// file: static/js/purchase.js
document.addEventListener("DOMContentLoaded", function () {
    const qtyInput = document.getElementById("SOLUONG_NHAP");
    const minusBtn = document.getElementById("qtyMinus");
    const plusBtn = document.getElementById("qtyPlus");

    if (qtyInput && minusBtn && plusBtn) {
        function getQty() {
            const value = parseInt(qtyInput.value || "1", 10);
            return isNaN(value) || value < 1 ? 1 : value;
        }

        minusBtn.addEventListener("click", function (e) {
            e.preventDefault();
            if (qtyInput.disabled) return;
            const current = getQty();
            qtyInput.value = Math.max(1, current - 1);
        });

        plusBtn.addEventListener("click", function (e) {
            e.preventDefault();
            if (qtyInput.disabled) return;
            const current = getQty();
            qtyInput.value = current + 1;
        });

        qtyInput.addEventListener("input", function () {
            let value = parseInt(qtyInput.value || "1", 10);
            if (isNaN(value) || value < 1) {
                qtyInput.value = 1;
            }
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const discountInput = document.getElementById("purchaseDiscountInput");
    const currentPurchaseInvoiceId = document.getElementById("currentPurchaseInvoiceId")?.value || "";
    if (!discountInput || !currentPurchaseInvoiceId || discountInput.disabled) return;

    const summaryTongSoLuong = document.getElementById("summaryTongSoLuong");
    const summaryChietKhauPercent = document.getElementById("summaryChietKhauPercent");
    const summaryTienChietKhau = document.getElementById("summaryTienChietKhau");
    const summaryCanThanhToan = document.getElementById("summaryCanThanhToan");

    function toNumber(value) {
        const n = parseFloat(value);
        return Number.isFinite(n) ? n : 0;
    }

    function clampDiscount(value) {
        if (value < 0) return 0;
        if (value > 100) return 100;
        return value;
    }

    function formatMoney(value) {
        return `${toNumber(value).toLocaleString("vi-VN")}đ`;
    }

    function formatPercent(value) {
        const n = toNumber(value);
        const rounded = Number.isInteger(n) ? n.toFixed(0) : n.toFixed(2).replace(/\.?0+$/, "");
        return `${rounded}%`;
    }

    function renderSummary(summary) {
        if (summaryTongSoLuong) {
            summaryTongSoLuong.textContent = toNumber(summary.tong_so_luong).toString();
        }
        if (summaryChietKhauPercent) {
            summaryChietKhauPercent.textContent = formatPercent(summary.chietkhau_percent);
        }
        if (summaryTienChietKhau) {
            summaryTienChietKhau.textContent = formatMoney(summary.tien_chiet_khau);
        }
        if (summaryCanThanhToan) {
            summaryCanThanhToan.textContent = formatMoney(summary.can_thanh_toan);
        }
    }

    let debounceTimer = null;
    let isUpdating = false;

    async function pushDiscountUpdate() {
        if (isUpdating) return;

        const discountValue = clampDiscount(toNumber(discountInput.value || 0));
        discountInput.value = discountValue;
        console.log("discount input:", discountValue);

        isUpdating = true;
        try {
            const response = await fetch("/purchase/update-discount", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    mahdn: currentPurchaseInvoiceId,
                    chietkhau: discountValue,
                }),
            });
            const result = await response.json();
            if (!response.ok || !result.success) {
                throw new Error(result.message || "Không thể cập nhật chiết khấu.");
            }
            renderSummary(result.purchase_summary || {});
        } catch (error) {
            console.error("Update discount failed:", error);
        } finally {
            isUpdating = false;
        }
    }

    discountInput.addEventListener("input", function () {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(pushDiscountUpdate, 300);
    });
    discountInput.addEventListener("change", pushDiscountUpdate);
    discountInput.addEventListener("blur", pushDiscountUpdate);
});

function validatePurchaseItem() {
    const input = document.getElementById('SOLUONG_NHAP');
    if (!input || input.disabled) return false;
    const sl = parseInt(input.value);
    if (!sl || sl <= 0) { 
        alert('Số lượng nhập phải lớn hơn 0!'); 
        return false; 
    }
    return true;
}

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('purchaseSearch');
    if (!searchInput) return;
    searchInput.addEventListener('input', () => {
        const active = document.querySelector('.filter-tab.active');
        const status = active?.dataset.filter || 'all';
        filterPurchaseProducts(active, status);
    });
});

function selectPurchaseProduct(maspct, stock = 0) {
    const input = document.getElementById('MASPCT');
    if (!input || input.disabled) return;
    console.log("Selected product for purchase:", maspct, stock);
    input.value = maspct;
    input.focus();
    
    const qtyInput = document.getElementById("SOLUONG_NHAP");
    if (qtyInput && (!qtyInput.value || parseInt(qtyInput.value) < 1)) {
        qtyInput.value = 1;
    }
}

function filterPurchaseProducts(btn, status) {
    if (btn) {
        document.querySelectorAll('.filter-tab').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
    }
    const q = (document.getElementById('purchaseSearch')?.value || '').toLowerCase();
    document.querySelectorAll('#purchaseProductBody .purchase-product-row').forEach((row) => {
        const matchStatus = status === 'all' || row.dataset.status === status;
        const matchQuery = !q || row.textContent.toLowerCase().includes(q);
        row.style.display = (matchStatus && matchQuery) ? '' : 'none';
    });
}
