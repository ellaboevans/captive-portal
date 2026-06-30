from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
import aiosqlite
import random
import string
import os

app = FastAPI(title="Captive Portal Auth Service")

DB_PATH = os.getenv("DB_PATH", "/data/portal.db")
SESSION_HOURS = int(os.getenv("SESSION_DURATION_HOURS", 24))
REQUIRE_VOUCHER = os.getenv("REQUIRE_VOUCHER", "false").lower() == "true"
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "changeme")


async def get_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS sessions (
            ip TEXT PRIMARY KEY,
            created_at TEXT,
            expires_at TEXT,
            voucher_code TEXT
        )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS vouchers (
            code TEXT PRIMARY KEY,
            duration_hours INTEGER,
            used INTEGER DEFAULT 0,
            created_at TEXT
        )""")
        await db.commit()
        yield db


@app.on_event("startup")
async def startup():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS sessions (
            ip TEXT PRIMARY KEY, created_at TEXT, expires_at TEXT, voucher_code TEXT)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS vouchers (
            code TEXT PRIMARY KEY, duration_hours INTEGER, used INTEGER DEFAULT 0, created_at TEXT)""")
        await db.commit()


@app.get("/api/check")
async def check_auth(x_real_ip: str = Header(None)):
    if not x_real_ip:
        raise HTTPException(status_code=401, detail="No IP")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT expires_at FROM sessions WHERE ip = ?", (x_real_ip,)
        ) as cursor:
            row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="Not authenticated")
    expires = datetime.fromisoformat(row[0])
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=None)
    if expires < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Session expired")
    return {"status": "authenticated"}


class AuthRequest(BaseModel):
    ip: str
    voucher: str | None = None


@app.post("/api/auth")
async def authenticate(body: AuthRequest):
    duration = SESSION_HOURS
    if REQUIRE_VOUCHER and not body.voucher:
        raise HTTPException(status_code=403, detail="Voucher required")
    if body.voucher:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT duration_hours, used FROM vouchers WHERE code = ?",
                (body.voucher.upper(),)
            ) as cursor:
                row = await cursor.fetchone()
            if not row or row[1] == 1:
                raise HTTPException(status_code=403, detail="Invalid or used voucher")
            duration = row[0]
            await db.execute(
                "UPDATE vouchers SET used = 1 WHERE code = ?", (body.voucher.upper(),)
            )
            await db.commit()

    expires = datetime.utcnow() + timedelta(hours=duration)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO sessions (ip, created_at, expires_at, voucher_code) VALUES (?, ?, ?, ?)",
            (body.ip, datetime.utcnow().isoformat(), expires.isoformat(), body.voucher)
        )
        await db.commit()

    return {"status": "authenticated", "expires_at": expires.isoformat()}


def require_admin(authorization: str = Header(None)):
    if not authorization or authorization != f"Bearer {ADMIN_SECRET}":
        raise HTTPException(status_code=403, detail="Unauthorized")


class RevokeRequest(BaseModel):
    ip: str


@app.post("/api/revoke")
async def revoke(body: RevokeRequest, _=Depends(require_admin)):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM sessions WHERE ip = ?", (body.ip,))
        await db.commit()
    return {"status": "revoked"}


@app.get("/api/sessions")
async def list_sessions(_=Depends(require_admin)):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT ip, created_at, expires_at FROM sessions") as cursor:
            rows = await cursor.fetchall()
    return [{"ip": r[0], "created_at": r[1], "expires_at": r[2]} for r in rows]


class VoucherRequest(BaseModel):
    count: int = 10
    duration_hours: int = 2


@app.post("/api/vouchers/generate")
async def generate_vouchers(body: VoucherRequest, _=Depends(require_admin)):
    codes = []
    async with aiosqlite.connect(DB_PATH) as db:
        for _ in range(body.count):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            await db.execute(
                "INSERT INTO vouchers (code, duration_hours, created_at) VALUES (?, ?, ?)",
                (code, body.duration_hours, datetime.utcnow().isoformat())
            )
            codes.append(code)
        await db.commit()
    return {"vouchers": codes}
