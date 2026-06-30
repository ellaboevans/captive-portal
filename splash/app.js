async function authenticate() {
  const voucher = document.getElementById('voucher').value.trim() || null;
  const status = document.getElementById('status');

  status.textContent = 'Connecting...';

  try {
    const res = await fetch('/api/auth', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ip: 'self', voucher })
    });

    const data = await res.json();

    if (res.ok) {
      status.textContent = '\u2705 Connected! Redirecting...';
      setTimeout(() => window.location.href = '/', 1500);
    } else {
      status.textContent = `\u274c ${data.detail || data.error || 'Authentication failed'}`;
    }
  } catch (err) {
    status.textContent = '\u274c Could not reach portal. Try again.';
  }
}
