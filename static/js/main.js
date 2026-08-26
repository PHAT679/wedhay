// file: static/js/main.js
// ── Auto-dismiss flash messages ──────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        document.querySelectorAll('.alert-flash').forEach(el => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
            bsAlert.close();
        });
    }, 4000);

    // Clock
    const clockEl = document.getElementById('currentTime');
    if (clockEl) {
        const tick = () => {
            const now = new Date();
            clockEl.textContent = now.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        };
        tick();
        setInterval(tick, 1000);
    }
});

// ── Sidebar toggle ────────────────────────────────────────────────
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const wrapper = document.querySelector('.main-wrapper');
    if (window.innerWidth <= 768) {
        sidebar.classList.toggle('show');
    } else {
        sidebar.classList.toggle('hidden');
        wrapper.classList.toggle('expanded');
    }
}

// ── Generic table search ──────────────────────────────────────────
function filterTable() {
    const q      = (document.getElementById('productSearch')?.value || '').toLowerCase();
    const status = (document.getElementById('statusFilter')?.value || '');
    const rows   = document.querySelectorAll('#productsBody tr');
    let visible  = 0;
    rows.forEach(row => {
        const matchQ = !q || row.dataset.search?.includes(q) || row.textContent.toLowerCase().includes(q);
        const matchS = !status || row.dataset.status === status;
        row.style.display = (matchQ && matchS) ? '' : 'none';
        if (matchQ && matchS) visible++;
    });
    const cnt = document.getElementById('rowCount');
    if (cnt) cnt.textContent = visible + ' sản phẩm';
}

function searchStock() {
    const q = (document.getElementById('stockSearch')?.value || '').toLowerCase();
    document.querySelectorAll('.stock-search-table tbody tr').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
}
