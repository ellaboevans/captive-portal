import urllib.request
import json
import datetime as dt

AUTH = "http://127.0.0.1:3000"
ADMIN = "changeme"
PASS = 0
FAIL = 0


def ok(name, cond):
    global PASS, FAIL
    if cond:
        print(f"  PASS: {name}")
        PASS += 1
    else:
        print(f"  FAIL: {name}")
        FAIL += 1


def req(method, path, headers=None, data=None):
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(f"{AUTH}{path}", data=body, headers=h, method=method)
    try:
        resp = urllib.request.urlopen(r)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


print("=== Auth Service Tests ===")
print()

status, _ = req("GET", "/api/check", {"X-Real-IP": "10.0.0.5"})
ok("Unauthenticated returns 401", status == 401)

status, data = req("POST", "/api/auth", data={"ip": "10.0.0.5"})
ok("Click-through auth succeeds", status == 200 and data["status"] == "authenticated")

status, data = req("GET", "/api/check", {"X-Real-IP": "10.0.0.5"})
ok("Authenticated check returns 200", status == 200)

status, data = req("POST", "/api/auth", data={"ip": "10.0.0.5"})
expires = dt.datetime.fromisoformat(data["expires_at"])
ok("Expiry is in the future", expires > dt.datetime.utcnow())

status, data = req("POST", "/api/vouchers/generate",
                   {"Authorization": f"Bearer {ADMIN}"},
                   {"count": 3, "duration_hours": 2})
ok("Vouchers generated", status == 200 and len(data["vouchers"]) == 3)
voucher = data["vouchers"][0]
print(f"       Voucher: {voucher}")

status, data = req("POST", "/api/auth", data={"ip": "10.0.0.6", "voucher": voucher})
ok("Voucher auth succeeds", status == 200 and data["status"] == "authenticated")

status, data = req("POST", "/api/auth", data={"ip": "10.0.0.7", "voucher": voucher})
ok("Duplicate voucher rejected", status == 403)

status, data = req("GET", "/api/sessions", {"Authorization": f"Bearer {ADMIN}"})
ok("Sessions list returned", status == 200 and len(data) >= 2)
ips = [s["ip"] for s in data]
ok("Session list has 10.0.0.5", "10.0.0.5" in ips)
ok("Session list has 10.0.0.6", "10.0.0.6" in ips)

status, data = req("POST", "/api/revoke",
                   {"Authorization": f"Bearer {ADMIN}"},
                   {"ip": "10.0.0.5"})
ok("Session revoked", status == 200 and data["status"] == "revoked")

status, _ = req("GET", "/api/check", {"X-Real-IP": "10.0.0.5"})
ok("Revoked returns 401", status == 401)

status, _ = req("GET", "/api/sessions")
ok("Admin endpoint rejects no auth", status == 403)

print()
print(f"=== Results: {PASS} passed, {FAIL} failed ===")
exit(FAIL)
