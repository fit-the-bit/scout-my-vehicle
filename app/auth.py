import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.database import get_db_connection

SESSION_COOKIE_NAME = "scout_admin_session"
SESSION_DURATION_DAYS = 7

def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    if not salt:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    return pwd_hash, salt

def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    pwd_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(pwd_hash, expected_hash)

def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires_at = (now + timedelta(days=SESSION_DURATION_DAYS)).isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sessions (session_token, user_id, created_at, expires_at)
        VALUES (?, ?, ?, ?);
    """, (token, user_id, now.isoformat(), expires_at))
    conn.commit()
    conn.close()
    return token

def get_user_from_session(session_token: Optional[str]) -> Optional[dict]:
    if not session_token:
        return None

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.username, u.name, u.role, u.dealership_id, s.expires_at, d.name as dealer_name, d.city as dealer_city
        FROM sessions s
        JOIN admin_users u ON s.user_id = u.id
        LEFT JOIN dealerships d ON u.dealership_id = d.id
        WHERE s.session_token = ?;
    """, (session_token,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    user = dict(row)
    try:
        expires_at = datetime.fromisoformat(user["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            delete_session(session_token)
            return None
    except Exception:
        pass

    return user

def delete_session(session_token: str):
    if not session_token:
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE session_token = ?;", (session_token,))
    conn.commit()
    conn.close()

def authenticate_user(username: str, password: str) -> Optional[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, username, password_hash, salt, name, role, dealership_id
        FROM admin_users
        WHERE LOWER(username) = LOWER(?);
    """, (username.strip(),))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    user = dict(row)
    if verify_password(password, user["salt"], user["password_hash"]):
        return user
    return None
