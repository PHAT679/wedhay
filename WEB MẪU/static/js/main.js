/**
 * Emmay Beauty - Main Client Interactivity (Vanilla JS)
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Password Visibility Toggle
  const togglePassBtns = document.querySelectorAll('.toggle-password');
  togglePassBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      const targetInputId = this.getAttribute('data-target') || 'id_password';
      const input = document.getElementById(targetInputId) || this.previousElementSibling;
      if (input) {
        if (input.type === 'password') {
          input.type = 'text';
          this.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
              <line x1="1" y1="1" x2="23" y2="23"></line>
            </svg>`;
        } else {
          input.type = 'password';
          this.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
              <circle cx="12" cy="12" r="3"></circle>
            </svg>`;
        }
      }
    });
  });

  // 2. Notification Dropdown Toggle
  const notifBtn = document.getElementById('notif-bell-btn');
  const notifDropdown = document.getElementById('notif-dropdown');
  if (notifBtn && notifDropdown) {
    notifBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      notifDropdown.classList.toggle('active');
    });

    document.addEventListener('click', function (e) {
      if (!notifDropdown.contains(e.target) && !notifBtn.contains(e.target)) {
        notifDropdown.classList.remove('active');
      }
    });
  }

  // 3. Modals Open / Close Helper
  window.openModal = function (modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  };

  window.closeModal = function (modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('active');
      document.body.style.overflow = 'auto';
    }
  };

  // Close modal when clicking outside box
  document.querySelectorAll('.modal-overlay').forEach(modal => {
    modal.addEventListener('click', function (e) {
      if (e.target === this) {
        this.classList.remove('active');
        document.body.style.overflow = 'auto';
      }
    });
  });

  // 4. Auto dismiss alerts after 5 seconds
  setTimeout(() => {
    document.querySelectorAll('.alert').forEach(al => {
      al.style.transition = 'opacity 0.5s ease';
      al.style.opacity = '0';
      setTimeout(() => al.remove(), 500);
    });
  }, 5000);
});

// Demo accounts filler
function fillDemo(username, password) {
  const userInput = document.getElementById('id_username') || document.querySelector('input[name="username"]');
  const passInput = document.getElementById('id_password') || document.querySelector('input[name="password"]');
  if (userInput && passInput) {
    userInput.value = username;
    passInput.value = password;
  }
}
