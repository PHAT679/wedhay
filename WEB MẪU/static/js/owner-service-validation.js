document.addEventListener('DOMContentLoaded', () => {
  const setupPriceFormatting = input => {
    input.type = 'text';
    input.inputMode = 'numeric';
    const format = () => {
      const original = input.value;
      if (!/^[\d.]*$/.test(original)) return;
      const cursorDigits = original.slice(0, input.selectionStart).replace(/\D/g, '').length;
      const digits = original.replace(/\./g, '');
      input.value = digits.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
      let cursor = 0;
      let count = 0;
      while (cursor < input.value.length && count < cursorDigits) {
        if (/\d/.test(input.value[cursor])) count++;
        cursor++;
      }
      input.setSelectionRange(cursor, cursor);
    };
    input.addEventListener('keydown', event => {
      if (input.selectionStart !== input.selectionEnd) return;
      const cursor = input.selectionStart;
      if (event.key === 'Backspace' && input.value[cursor - 1] === '.' && cursor > 1) {
        event.preventDefault();
        input.setRangeText('', cursor - 2, cursor, 'start');
        input.dispatchEvent(new Event('input', { bubbles: true }));
      } else if (event.key === 'Delete' && input.value[cursor] === '.' && cursor + 1 < input.value.length) {
        event.preventDefault();
        input.setRangeText('', cursor, cursor + 2, 'start');
        input.dispatchEvent(new Event('input', { bubbles: true }));
      }
    });
    input.addEventListener('input', format);
    format();
    return () => input.value.replace(/\./g, '');
  };
  const names = document.getElementById('service-existing-names');
  if (names) {
    const existing = new Set(JSON.parse(names.textContent));
    const field = document.getElementById('service-create-name-field');
    const input = field.querySelector('input');
    const error = document.getElementById('service-create-duplicate');
    const normalize = value => value.normalize('NFKC').trim().replace(/\s+/gu, ' ').toLowerCase();
    const validateName = () => {
      const duplicate = input.value.trim() !== '' && existing.has(normalize(input.value));
      field.querySelectorAll('[data-server-name-error]').forEach(item => item.remove());
      error.hidden = !duplicate;
      field.classList.toggle('has-error', duplicate || !!field.querySelector('[data-server-name-error]'));
      return !duplicate;
    };
    const priceField = document.getElementById('service-create-price-field');
    const priceInput = priceField.querySelector('input');
    const priceError = document.getElementById('service-create-price-error');
    const priceValue = setupPriceFormatting(priceInput);
    const validatePrice = () => {
      const value = priceValue().trim();
      const invalid = priceInput.validity.badInput || (value !== '' && (!/^[0-9]+$/.test(value) || !Number.isFinite(Number(value)) || Number(value) <= 0 || !Number.isInteger(Number(value))));
      priceField.querySelectorAll('[data-server-create-price-error]').forEach(item => item.remove());
      priceError.hidden = !invalid;
      priceField.classList.toggle('has-error', invalid);
      return !invalid;
    };
    input.addEventListener('input', validateName);
    priceInput.addEventListener('input', validatePrice);
    input.form.addEventListener('submit', event => {
      const nameValid = validateName();
      const priceValid = validatePrice();
      if (!nameValid || !priceValid) event.preventDefault();
      else priceInput.value = priceValue();
    });
  }
  const editForm = document.getElementById('service-edit-form');
  if (editForm) {
    const field = document.getElementById('service-edit-price-field');
    const input = field.querySelector('input');
    const error = document.getElementById('service-edit-price-error');
    const priceValue = setupPriceFormatting(input);
    const nameField = document.getElementById('service-edit-name-field');
    const nameInput = nameField.querySelector('input');
    const nameError = document.getElementById('service-edit-name-error');
    const validateName = () => {
      const valid = nameInput.value.trim() !== '';
      nameField.querySelectorAll('[data-server-edit-name-error]').forEach(item => item.remove());
      nameError.hidden = valid;
      nameField.classList.toggle('has-error', !valid);
      return valid;
    };
    const validatePrice = () => {
      const value = priceValue().trim();
      const valid = value !== '' && /^[0-9]+$/.test(value) && Number.isFinite(Number(value)) && Number(value) > 0 && Number.isInteger(Number(value));
      field.querySelectorAll('[data-server-price-error]').forEach(item => item.remove());
      error.hidden = valid;
      field.classList.toggle('service-edit-price-invalid', !valid);
      field.classList.toggle('has-error', !valid);
      return valid;
    };
    nameInput.addEventListener('input', validateName);
    input.addEventListener('input', validatePrice);
    input.addEventListener('blur', validatePrice);
    editForm.addEventListener('submit', event => {
      const nameValid = validateName();
      const priceValid = validatePrice();
      if (!nameValid || !priceValid) event.preventDefault();
      else input.value = priceValue();
    });
  }
});
