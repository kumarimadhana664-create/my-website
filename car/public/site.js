async function submitToApi(form) {
  const status = form.querySelector('[data-form-status]');
  const button = form.querySelector('button[type="submit"]');
  status.textContent = 'Sending...';
  button.disabled = true;

  try {
    const response = await fetch(form.dataset.endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(Object.fromEntries(new FormData(form)))
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Something went wrong.');
    form.reset();
    status.textContent = result.message;
  } catch (error) {
    status.textContent = error.message;
  } finally {
    button.disabled = false;
  }
}

document.querySelectorAll('[data-api-form]').forEach((form) => {
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    submitToApi(form);
  });
});