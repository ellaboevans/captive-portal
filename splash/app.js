async function authenticate() {
  const btn = document.getElementById('connectBtn');
  const btnText = document.getElementById('btnText');
  const spinner = document.getElementById('btnSpinner');
  const status = document.getElementById('status');
  const voucher = document.getElementById('voucher')?.value?.trim().toUpperCase() || null;

  btn.disabled = true;
  btnText.style.display = 'none';
  spinner.style.display = 'inline-block';
  status.className = 'status';
  status.textContent = 'Connecting...';

  try {
    const res = await fetch('/api/auth', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ip: 'self', voucher })
    });
    const data = await res.json();
    if (res.ok) {
      status.className = 'status success';
      status.textContent = '\u2713 Connected! Redirecting...';
      setTimeout(() => { window.location.href = '/'; }, 1500);
    } else {
      status.className = 'status error';
      status.textContent = '\u2717 ' + (data.detail || data.error || 'Authentication failed');
      btn.disabled = false;
      btnText.style.display = 'inline';
      spinner.style.display = 'none';
    }
  } catch (err) {
    status.className = 'status error';
    status.textContent = '\u2717 Could not reach portal. Try again.';
    btn.disabled = false;
    btnText.style.display = 'inline';
    spinner.style.display = 'none';
  }
}
