# Captive Portal Frontend Design

> **Status:** Approved design doc

**Goal:** Build a branded splash page for portal users and an admin dashboard for managing sessions and vouchers.

**Architecture:** Two static HTML applications served by nginx. Splash at `/splash/`, admin at `/admin/`. Both are vanilla HTML/CSS/JS — no build tools, no frameworks. The admin dashboard calls the auth service API directly (proxied through nginx at `/api/`).

**Tech Stack:** Vanilla HTML5, CSS3, ES6. No dependencies. Served by nginx:alpine.

---

## Splash Page (`/splash/`)

### Visual Design

- Full-screen dark gradient background (`#0a0a0f` → `#1a1a2e` → `#0f3460`)
- Subtle animated particle/grid background (CSS-only, no canvas/JS)
- Glass-morphism card (`background: rgba(255,255,255,0.05)`, `backdrop-filter: blur(20px)`)
- Wi-Fi signal icon (SVG inline, pulsing animation)
- "Guest Wi-Fi" title (placeholder, easily customizable)
- Light text on dark background
- Responsive: mobile-first, max-width 420px card

### States & Transitions

| State | Trigger | UI |
|---|---|---|
| Initial | Page load | Card with title, message, voucher input, connect button |
| Loading | Click "Connect Now" | Button shows spinner, status text "Connecting..." |
| Success | Auth API returns 200 | Green checkmark animation, "Connected! Redirecting..." |
| Error | Auth API returns 403/error | Red message with error text, button re-enabled |
| Voucher mode | `REQUIRE_VOUCHER=true` | Voucher input visible, button disabled until voucher entered |

### Components

1. **Background** — Full viewport dark gradient with CSS-only animated grid overlay
2. **Card** — Centered glass card with subtle border
3. **Wi-Fi icon** — Inline SVG with pulse animation
4. **Title** — "Guest Wi-Fi" heading
5. **Subtitle** — "Accept the terms below to connect to the internet."
6. **Terms text** — Brief acceptance text with clickable link
7. **Voucher input** — Text input, only visible when voucher mode is active
8. **Connect button** — Full-width, accent color (`#2563eb`), loading spinner on click
9. **Status area** — Success/error message below button
10. **Footer** — Small "Powered by Captive Portal" text

### API Integration

- `POST /api/auth` with `{ ip: "self", voucher: "..." }`
- On success: `window.location.href = "/"` after 1.5s delay
- On error: display error message from response

---

## Admin Dashboard (`/admin/`)

### Visual Design

- Same dark theme as splash page
- Two-panel layout: slim sidebar (240px) + main content area
- Sidebar: logo/title at top, navigation items (Sessions, Vouchers), logout at bottom
- Content area: header with page title, then data table or form

### Authentication

- Login screen at `/admin/login` — simple token input
- User enters `ADMIN_SECRET` value
- Token stored in `sessionStorage`
- All API calls include `Authorization: Bearer <token>` header
- If API returns 403, redirect to login

### Screens

#### Sessions Screen (`/admin/`)

- Active sessions table with columns: IP Address, Created At, Expires At, Action
- "Revoke" button per row — calls `POST /api/revoke`
- After revoke, row is removed with fade-out animation
- Auto-refresh every 30 seconds
- Empty state: "No active sessions" message
- Loading state: skeleton rows while fetching

#### Vouchers Screen (`/admin/vouchers`)

- Generate form:
  - Count input (number, default 10, min 1, max 100)
  - Duration input (number, default 2, unit: hours)
  - "Generate" button
- Generated codes displayed in a scrollable list
- Each code has a copy-to-clipboard button
- Success/error toasts for actions

### API Integration

| Action | Endpoint |
|---|---|
| List sessions | `GET /api/sessions` |
| Revoke session | `POST /api/revoke { "ip": "..." }` |
| Generate vouchers | `POST /api/vouchers/generate { "count": N, "duration_hours": N }` |

---

## Files

```
splash/
├── index.html          # Splash page (full app in one file)
├── style.css           # Splash styles
└── app.js              # Splash logic

admin/
├── index.html          # Dashboard shell (SPA router)
├── style.css           # Dashboard styles
├── app.js              # Dashboard logic (auth, API calls)
└── login.html          # Login page
```

---

## Nginx Changes

Add new location blocks to serve admin static files:

```nginx
location /admin/ {
    auth_request off;
    alias /usr/share/nginx/html/admin/;
}

location = /admin {
    return 302 /admin/;
}
```

---

## Testing

| Test | How | Expected |
|---|---|---|
| Splash loads | Browser → `http://<host>/splash` | Dark card layout renders |
| Connect flow | Click "Connect Now" | Success state, redirect |
| Voucher mode | Set `REQUIRE_VOUCHER=true`, restart | Voucher input shown |
| Admin login | Enter wrong token | Error message |
| Admin login | Enter correct `ADMIN_SECRET` | Dashboard loads |
| List sessions | Navigate to Sessions | Table with data |
| Revoke session | Click revoke | Row fades out |
| Generate vouchers | Fill form, click generate | Codes displayed with copy button |
