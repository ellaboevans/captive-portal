# Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a dark & modern splash page and admin dashboard for the captive portal.

**Architecture:** Two static vanilla HTML/CSS/JS apps served by nginx. Splash at `/splash/`, admin at `/admin/`. Admin calls auth API through nginx proxy.

**Tech Stack:** Vanilla HTML5, CSS3, ES6. No frameworks, no build tools.

## Global Constraints

- All new files go in `splash/` (modify existing) or `admin/` (new directory)
- No dependencies, no CDN links, no build step
- Dark theme throughout (#0a0a0f, #1a1a2e, #0f3460 palette)
- Mobile-first responsive
- Admin auth via `Authorization: Bearer` header with token from login form
- Admin SPA uses hash-based routing (`#sessions`, `#vouchers`)

---

### Task 1: Splash Page Redesign

**Files:**
- Modify: `splash/index.html`
- Modify: `splash/style.css`
- Modify: `splash/app.js`

- [ ] **Step 1: Write `splash/index.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Guest Wi-Fi</title>
  <link rel="stylesheet" href="/splash/style.css">
</head>
<body>
  <div class="bg-grid"></div>
  <div class="portal-card">
    <svg class="wifi-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><circle cx="12" cy="20" r="1"/>
    </svg>
    <h1>Guest Wi-Fi</h1>
    <p class="subtitle">Accept the terms below to connect to the internet.</p>
    <p class="terms">By connecting, you agree to our <a href="#">acceptable use policy</a>.</p>
    <div class="voucher-field" id="voucherField" style="display:none">
      <input type="text" id="voucher" placeholder="Voucher code" autocomplete="off">
    </div>
    <button id="connectBtn" onclick="authenticate()">
      <span id="btnText">Connect Now</span>
      <span id="btnSpinner" class="spinner" style="display:none"></span>
    </button>
    <p id="status" class="status"></p>
  </div>
  <p class="footer">Powered by Captive Portal</p>
  <script src="/splash/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Write `splash/style.css`**

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #0f3460 100%);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #e0e0e0;
  position: relative;
  overflow: hidden;
}
.bg-grid {
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  z-index: 0;
}
.portal-card {
  position: relative;
  z-index: 1;
  background: rgba(255,255,255,0.05);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 20px;
  padding: 40px 32px;
  width: 100%;
  max-width: 400px;
  margin: 20px;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.wifi-icon {
  width: 48px;
  height: 48px;
  color: #2563eb;
  margin-bottom: 16px;
  animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.05); }
}
h1 { font-size: 26px; font-weight: 700; margin-bottom: 8px; color: #fff; }
.subtitle { font-size: 14px; color: #94a3b8; margin-bottom: 20px; line-height: 1.5; }
.terms { font-size: 12px; color: #64748b; margin-bottom: 24px; }
.terms a { color: #60a5fa; text-decoration: none; }
.terms a:hover { text-decoration: underline; }
.voucher-field { margin-bottom: 16px; }
.voucher-field input {
  width: 100%;
  padding: 12px 16px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 10px;
  font-size: 15px;
  color: #fff;
  outline: none;
  transition: border-color 0.2s;
  text-align: center;
  letter-spacing: 2px;
  text-transform: uppercase;
}
.voucher-field input:focus { border-color: #2563eb; }
.voucher-field input::placeholder { color: #475569; letter-spacing: 0; text-transform: none; }
button {
  width: 100%;
  padding: 14px 24px;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
button:hover { background: #1d4ed8; }
button:active { transform: scale(0.98); }
button:disabled { opacity: 0.5; cursor: not-allowed; }
.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }
.status {
  margin-top: 16px;
  font-size: 14px;
  min-height: 20px;
  transition: all 0.3s;
}
.status.success { color: #4ade80; }
.status.error { color: #f87171; }
.footer {
  position: relative;
  z-index: 1;
  margin-top: 24px;
  font-size: 11px;
  color: #475569;
}
```

- [ ] **Step 3: Write `splash/app.js`**

```javascript
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
```

- [ ] **Step 4: Restart nginx and verify**

```bash
# Copy to gateway VM and restart
cd /home/ubuntu/captive-portal && git pull
sudo docker compose restart nginx
# Test from browser: http://192.168.252.4/splash
```

- [ ] **Step 5: Commit**

```bash
git add splash/ && git commit -m "feat: dark modern splash page redesign"
```

### Task 2: Admin Dashboard

**Files:**
- Create: `admin/login.html`
- Create: `admin/index.html`
- Create: `admin/style.css`
- Create: `admin/app.js`

- [ ] **Step 1: Create `admin/login.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Admin Login</title>
  <link rel="stylesheet" href="/admin/style.css">
</head>
<body class="login-page">
  <div class="login-card">
    <h1>Admin</h1>
    <p>Enter your admin token to continue.</p>
    <input type="password" id="tokenInput" placeholder="Admin token" autocomplete="off">
    <button onclick="login()">Sign In</button>
    <p id="loginError" class="status error"></p>
  </div>
  <script src="/admin/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Create `admin/index.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dashboard — Captive Portal</title>
  <link rel="stylesheet" href="/admin/style.css">
</head>
<body>
  <aside class="sidebar">
    <div class="sidebar-brand">Captive Portal</div>
    <nav class="sidebar-nav">
      <a href="#sessions" class="nav-item active" data-view="sessions">Sessions</a>
      <a href="#vouchers" class="nav-item" data-view="vouchers">Vouchers</a>
    </nav>
    <button class="logout-btn" onclick="logout()">Sign Out</button>
  </aside>
  <main class="main-content">
    <div id="view-sessions" class="view active">
      <h2>Sessions</h2>
      <div id="sessionsTableWrap">
        <table id="sessionsTable">
          <thead><tr><th>IP Address</th><th>Created</th><th>Expires</th><th>Action</th></tr></thead>
          <tbody id="sessionsBody"></tbody>
        </table>
      </div>
      <p id="sessionsEmpty" class="empty-state">No active sessions.</p>
    </div>
    <div id="view-vouchers" class="view">
      <h2>Generate Vouchers</h2>
      <div class="voucher-form">
        <label>Count: <input type="number" id="voucherCount" value="10" min="1" max="100"></label>
        <label>Duration (hours): <input type="number" id="voucherDuration" value="2" min="1" max="168"></label>
        <button onclick="generateVouchers()">Generate</button>
      </div>
      <div id="voucherResults" style="display:none">
        <h3>Generated Codes</h3>
        <ul id="voucherList"></ul>
      </div>
      <p id="voucherStatus" class="status"></p>
    </div>
  </main>
  <script src="/admin/app.js"></script>
</body>
</html>
```

- [ ] **Step 3: Create `admin/style.css`**

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: #0a0a0f;
  color: #e0e0e0;
  min-height: 100vh;
}
a { color: #60a5fa; text-decoration: none; }

/* Login */
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
}
.login-card {
  background: rgba(255,255,255,0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 20px;
  padding: 40px 32px;
  max-width: 360px;
  width: 100%;
  margin: 20px;
  text-align: center;
}
.login-card h1 { font-size: 24px; margin-bottom: 8px; color: #fff; }
.login-card p { font-size: 14px; color: #94a3b8; margin-bottom: 24px; }
.login-card input {
  width: 100%;
  padding: 12px 16px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 10px;
  font-size: 15px;
  color: #fff;
  outline: none;
  margin-bottom: 16px;
}
.login-card input:focus { border-color: #2563eb; }
.login-card button {
  width: 100%;
  padding: 12px;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}
.login-card button:hover { background: #1d4ed8; }

/* Dashboard layout */
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 220px;
  background: #111118;
  border-right: 1px solid rgba(255,255,255,0.06);
  display: flex;
  flex-direction: column;
  padding: 24px 0;
}
.sidebar-brand {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  padding: 0 20px 24px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.sidebar-nav { flex: 1; padding: 16px 0; }
.nav-item {
  display: block;
  padding: 10px 20px;
  color: #94a3b8;
  font-size: 14px;
  transition: all 0.15s;
}
.nav-item:hover, .nav-item.active { color: #fff; background: rgba(255,255,255,0.04); }
.logout-btn {
  margin: 0 12px;
  padding: 10px;
  background: transparent;
  color: #64748b;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
}
.logout-btn:hover { color: #f87171; border-color: rgba(248,113,113,0.3); }

/* Main */
.main-content {
  margin-left: 220px;
  padding: 32px 40px;
}
.main-content h2 { font-size: 22px; color: #fff; margin-bottom: 20px; }
.view { display: none; }
.view.active { display: block; }

/* Table */
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th { text-align: left; padding: 12px 16px; color: #64748b; font-weight: 500; border-bottom: 1px solid rgba(255,255,255,0.08); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
td { padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); }
tr:hover td { background: rgba(255,255,255,0.02); }
.revoke-btn {
  padding: 6px 14px;
  background: transparent;
  color: #f87171;
  border: 1px solid rgba(248,113,113,0.3);
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}
.revoke-btn:hover { background: rgba(248,113,113,0.1); }
.empty-state { color: #64748b; font-size: 14px; padding: 40px 0; text-align: center; }

/* Voucher form */
.voucher-form { display: flex; gap: 16px; align-items: flex-end; margin-bottom: 24px; flex-wrap: wrap; }
.voucher-form label { font-size: 13px; color: #94a3b8; display: flex; flex-direction: column; gap: 6px; }
.voucher-form input {
  padding: 10px 14px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 8px;
  font-size: 14px;
  color: #fff;
  outline: none;
  width: 100px;
}
.voucher-form input:focus { border-color: #2563eb; }
.voucher-form button {
  padding: 10px 24px;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
#voucherResults { margin-top: 20px; }
#voucherResults h3 { font-size: 14px; color: #94a3b8; margin-bottom: 12px; }
#voucherList {
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
#voucherList li {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  padding: 8px 16px;
  font-family: monospace;
  font-size: 14px;
  letter-spacing: 1px;
  color: #4ade80;
  cursor: pointer;
  transition: all 0.15s;
}
#voucherList li:hover { background: rgba(255,255,255,0.1); }
#voucherList li.copied::after { content: ' Copied!'; color: #60a5fa; font-size: 11px; }
.status { font-size: 14px; margin-top: 16px; }
.status.error { color: #f87171; }
.status.success { color: #4ade80; }

@media (max-width: 768px) {
  .sidebar { width: 100%; position: relative; height: auto; flex-direction: row; align-items: center; padding: 12px 16px; }
  .sidebar-brand { padding: 0; border: none; margin-right: 20px; }
  .sidebar-nav { display: flex; gap: 0; padding: 0; flex: 1; }
  .nav-item { padding: 8px 14px; }
  .logout-btn { margin: 0; }
  .main-content { margin-left: 0; padding: 20px; }
}
```

- [ ] **Step 4: Create `admin/app.js`**

```javascript
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
    headers: apiHeaders(),
    ...options
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
  fetch(API + '/api/sessions', { headers: { 'Authorization': 'Bearer ' + token } })
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
    tr.innerHTML = `
      <td>${s.ip}</td>
      <td>${new Date(s.created_at).toLocaleString()}</td>
      <td>${new Date(s.expires_at).toLocaleString()}</td>
      <td><button class="revoke-btn" onclick="revokeSession('${s.ip}')">Revoke</button></td>
    `;
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
    data.vouchers.forEach(code => {
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
```

- [ ] **Step 5: Commit**

```bash
git add admin/ && git commit -m "feat: admin dashboard with sessions and voucher management"
```

### Task 3: Nginx + Docker Compose Config

**Files:**
- Modify: `nginx/nginx.conf`
- Modify: `docker-compose.yml`

- [ ] **Step 1: Add admin location to `nginx/nginx.conf`**

Add before the closing `}` of the server block:

```nginx
        location /admin/ {
            auth_request off;
            alias /usr/share/nginx/html/admin/;
        }
```

- [ ] **Step 2: Add admin volume mount to `docker-compose.yml`**

```yaml
      - ./admin:/usr/share/nginx/html/admin:ro
```

- [ ] **Step 3: Restart nginx**

```bash
cd /home/ubuntu/captive-portal && git pull
sudo docker compose up -d --build nginx
```

- [ ] **Step 4: Verify**

```bash
# Splash page loads with new design
curl -s http://localhost/splash | head -5 | grep 'Guest Wi-Fi'
# Admin login loads
curl -s http://localhost/admin/login.html | head -5 | grep 'Admin Login'
# Admin dashboard loads
curl -s http://localhost/admin/ | head -5 | grep 'Dashboard'
```

- [ ] **Step 5: Commit**

```bash
git add nginx/ docker-compose.yml && git commit -m "feat: serve admin dashboard via nginx"
```
