// file: static/js/product.js
document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.querySelector('input[name="q"]');
    
    if (searchInput) {
        let timer;
        searchInput.addEventListener("input", function () {
            clearTimeout(timer);
            timer = setTimeout(() => {
                this.form.submit();
            }, 500);
        });
    }
});
