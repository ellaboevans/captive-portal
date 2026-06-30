const API = '/api';
const TOKEN_KEY = 'portal_admin_token';

function getToken() { return sessionStorage.getItem(TOKEN_KEY); }

function setToken(t) { sessionStorage.setItem(TOKEN_KEY, t); }

function clearToken() { sessionStorage.removeItem(TOKEN_KEY); }

function apiHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + getToken()
  };
}

async function api(path, options = {}) {
  const res = await fetch(API + path, {
    ...options,
    headers: { ...apiHeaders(), ...options.headers }
  });
  if (res.status === 403) {
    clearToken();
    window.location.href = '/admin/login.html';
    return null;
  }
  return res;
}

// Login
function login() {
  const token = document.getElementById('tokenInput').value.trim();
  if (!token) return;
  setToken(token);
  fetch(API + '/sessions', { headers: { 'Authorization': 'Bearer ' + token } })
    .then(r => {
      if (r.ok) { window.location.href = '/admin/'; }
      else {
        clearToken();
        document.getElementById('loginError').textContent = 'Invalid token';
      }
    })
    .catch(() => {
      clearToken();
      document.getElementById('loginError').textContent = 'Could not reach server';
    });
}

document.getElementById('tokenInput')?.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') login();
});

// Logout
function logout() {
  clearToken();
  window.location.href = '/admin/login.html';
}

// Dashboard
let sessionsInterval = null;

function navigate() {
  const hash = window.location.hash.slice(1) || 'sessions';
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const view = document.getElementById('view-' + hash);
  if (view) view.classList.add('active');
  const nav = document.querySelector(`.nav-item[data-view="${hash}"]`);
  if (nav) nav.classList.add('active');
  if (hash === 'sessions') loadSessions();
}

window.addEventListener('hashchange', navigate);

// Sessions
async function loadSessions() {
  const res = await api('/sessions');
  if (!res) return;
  const sessions = await res.json();
  const tbody = document.getElementById('sessionsBody');
  const empty = document.getElementById('sessionsEmpty');
  tbody.innerHTML = '';
  if (sessions.length === 0) {
    empty.style.display = 'block';
    return;
  }
  empty.style.display = 'none';
  sessions.forEach(s => {
    const tr = document.createElement('tr');
    tr.id = 'session-' + s.ip.replace(/\./g, '-');
    const tdIp = document.createElement('td');
    tdIp.textContent = s.ip;
    const tdCreated = document.createElement('td');
    tdCreated.textContent = new Date(s.created_at).toLocaleString();
    const tdExpires = document.createElement('td');
    tdExpires.textContent = new Date(s.expires_at).toLocaleString();
    const tdAction = document.createElement('td');
    const revokeBtn = document.createElement('button');
    revokeBtn.className = 'revoke-btn';
    revokeBtn.textContent = 'Revoke';
    revokeBtn.onclick = () => revokeSession(s.ip);
    tdAction.appendChild(revokeBtn);
    tr.appendChild(tdIp);
    tr.appendChild(tdCreated);
    tr.appendChild(tdExpires);
    tr.appendChild(tdAction);
    tbody.appendChild(tr);
  });
}

async function revokeSession(ip) {
  const res = await api('/revoke', {
    method: 'POST',
    body: JSON.stringify({ ip })
  });
  if (res && res.ok) {
    const row = document.getElementById('session-' + ip.replace(/\./g, '-'));
    if (row) row.style.opacity = '0.3';
    setTimeout(() => { if (row) row.remove(); }, 300);
  } else if (res) {
    const data = await res.json().catch(() => ({}));
    alert(data.detail || 'Failed to revoke session');
  } else {
    alert('Could not reach server');
  }
}

// Vouchers
async function generateVouchers() {
  const count = parseInt(document.getElementById('voucherCount').value) || 10;
  const duration = parseInt(document.getElementById('voucherDuration').value) || 2;
  const status = document.getElementById('voucherStatus');
  const results = document.getElementById('voucherResults');
  const list = document.getElementById('voucherList');
  status.className = 'status';
  status.textContent = 'Generating...';
  results.style.display = 'none';
  list.innerHTML = '';
  const res = await api('/vouchers/generate', {
    method: 'POST',
    body: JSON.stringify({ count, duration_hours: duration })
  });
  if (!res) return;
  const data = await res.json();
  if (res.ok) {
    status.className = 'status success';
    status.textContent = count + ' vouchers generated';
    results.style.display = 'block';
    (data.vouchers || []).forEach(code => {
      const li = document.createElement('li');
      li.textContent = code;
      li.title = 'Click to copy';
      li.onclick = () => {
        navigator.clipboard.writeText(code).then(() => {
          li.classList.add('copied');
          setTimeout(() => li.classList.remove('copied'), 1500);
        });
      };
      list.appendChild(li);
    });
  } else {
    status.className = 'status error';
    status.textContent = data.detail || 'Failed to generate';
  }
}

// Init
if (window.location.pathname === '/admin/' || window.location.pathname === '/admin/index.html') {
  if (!getToken()) { window.location.href = '/admin/login.html'; }
  else {
    navigate();
    sessionsInterval = setInterval(loadSessions, 30000);
    window.addEventListener('beforeunload', () => {
      if (sessionsInterval) clearInterval(sessionsInterval);
    });
  }
}
