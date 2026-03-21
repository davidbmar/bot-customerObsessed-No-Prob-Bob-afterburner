"""SQLite database — users, auth sessions, and user preferences.

Uses WAL journal mode for safe concurrent access from threaded HTTP handlers.
Ported from iphone-and-companion-transcribe-mode/gateway/db.py.
"""

from __future__ import annotations

import json
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone as _tz
from pathlib import Path

DB_PATH: Path = Path(__file__).resolve().parent.parent / "data" / "bot.db"


def _utcnow() -> str:
    return datetime.now(_tz.utc).isoformat()


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    google_id       TEXT UNIQUE NOT NULL,
    email           TEXT,
    name            TEXT,
    avatar_url      TEXT,
    role            TEXT DEFAULT 'user',
    created_at      TEXT,
    last_login      TEXT
);

CREATE TABLE IF NOT EXISTS user_preferences (
    user_id         INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    voice           TEXT,
    llm_provider    TEXT,
    llm_model       TEXT,
    custom_instructions TEXT,
    search_enabled  INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS auth_sessions (
    token           TEXT PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at      TEXT,
    expires_at      TEXT,
    last_used       TEXT
);

CREATE TABLE IF NOT EXISTS conversations (
    id              TEXT PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id) ON DELETE CASCADE,
    started_at      TEXT,
    ended_at        TEXT,
    title           TEXT,
    personality     TEXT,
    llm_model       TEXT,
    turn_count      INTEGER DEFAULT 0
);
"""


def init_db() -> None:
    conn = _connect()
    try:
        conn.executescript(_SCHEMA)
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def upsert_user(google_id: str, email: str, name: str, avatar_url: str) -> int:
    now = _utcnow()
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT id FROM users WHERE google_id = ?", (google_id,)
        ).fetchone()
        if row:
            conn.execute(
                "UPDATE users SET email = ?, name = ?, avatar_url = ?, last_login = ? "
                "WHERE id = ?",
                (email, name, avatar_url, now, row["id"]),
            )
            conn.commit()
            return row["id"]
        else:
            cur = conn.execute(
                "INSERT INTO users (google_id, email, name, avatar_url, created_at, last_login) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (google_id, email, name, avatar_url, now, now),
            )
            conn.commit()
            return cur.lastrowid  # type: ignore[return-value]
    finally:
        conn.close()


def get_user(user_id: int) -> dict | None:
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# User Preferences
# ---------------------------------------------------------------------------

def get_user_preferences(user_id: int) -> dict | None:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT * FROM user_preferences WHERE user_id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_user_preferences(user_id: int, **kwargs) -> None:
    allowed = {"voice", "llm_provider", "llm_model", "custom_instructions", "search_enabled"}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return
    conn = _connect()
    try:
        existing = conn.execute(
            "SELECT user_id FROM user_preferences WHERE user_id = ?", (user_id,)
        ).fetchone()
        if existing:
            set_clause = ", ".join(f"{col} = ?" for col in fields)
            values = list(fields.values()) + [user_id]
            conn.execute(
                f"UPDATE user_preferences SET {set_clause} WHERE user_id = ?", values
            )
        else:
            fields["user_id"] = user_id
            cols = ", ".join(fields.keys())
            placeholders = ", ".join("?" for _ in fields)
            conn.execute(
                f"INSERT INTO user_preferences ({cols}) VALUES ({placeholders})",
                list(fields.values()),
            )
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Auth Sessions
# ---------------------------------------------------------------------------

def create_auth_session(user_id: int, ttl_hours: int = 168) -> str:
    """Create a session token valid for ttl_hours (default 7 days)."""
    token = secrets.token_urlsafe(32)
    now = datetime.now(_tz.utc)
    expires = now + timedelta(hours=ttl_hours)
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO auth_sessions (token, user_id, created_at, expires_at, last_used) "
            "VALUES (?, ?, ?, ?, ?)",
            (token, user_id, now.isoformat(), expires.isoformat(), now.isoformat()),
        )
        conn.commit()
    finally:
        conn.close()
    return token


def validate_auth_session(token: str) -> int | None:
    """Validate a session token. Returns user_id if valid, None if expired/missing."""
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT user_id, expires_at FROM auth_sessions WHERE token = ?", (token,)
        ).fetchone()
        if not row:
            return None
        expires = datetime.fromisoformat(row["expires_at"])
        if datetime.now(_tz.utc) > expires:
            conn.execute("DELETE FROM auth_sessions WHERE token = ?", (token,))
            conn.commit()
            return None
        conn.execute(
            "UPDATE auth_sessions SET last_used = ? WHERE token = ?",
            (_utcnow(), token),
        )
        conn.commit()
        return row["user_id"]
    finally:
        conn.close()


def delete_auth_session(token: str) -> None:
    conn = _connect()
    try:
        conn.execute("DELETE FROM auth_sessions WHERE token = ?", (token,))
        conn.commit()
    finally:
        conn.close()


def cleanup_expired_sessions() -> int:
    conn = _connect()
    try:
        now = _utcnow()
        cur = conn.execute("DELETE FROM auth_sessions WHERE expires_at < ?", (now,))
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()
