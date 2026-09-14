"""User activity logging and audit trail for AgriSmart.

Records authentication events, profile changes, and API access
for security monitoring and compliance tracking.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

DB_DIR = Path(__file__).resolve().parents[1] / "data"
AUDIT_DB_PATH = DB_DIR / "audit.db"

logger = logging.getLogger("agrismart.audit")


# ---------------------------------------------------------------------------
# Audit event types
# ---------------------------------------------------------------------------

class AuditEvent:
    """Constants for audit event types."""
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    SIGNUP = "SIGNUP"
    LOGOUT = "LOGOUT"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    LOCATION_UPDATE = "LOCATION_UPDATE"
    PROFILE_UPDATE = "PROFILE_UPDATE"
    PREDICTION_REQUEST = "PREDICTION_REQUEST"
    CHAT_REQUEST = "CHAT_REQUEST"
    RATE_LIMIT_HIT = "RATE_LIMIT_HIT"
    SESSION_EXPIRED = "SESSION_EXPIRED"


# ---------------------------------------------------------------------------
# Database initialization
# ---------------------------------------------------------------------------

def init_audit_db() -> None:
    """Initialize the SQLite audit log table."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(AUDIT_DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                username TEXT,
                ip_address TEXT,
                details TEXT,
                user_agent TEXT,
                success INTEGER DEFAULT 1
            )
        """)
        # Create index for efficient username queries
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_username
            ON audit_log (username, timestamp)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_event_type
            ON audit_log (event_type, timestamp)
        """)
        conn.commit()


# ---------------------------------------------------------------------------
# Logging functions
# ---------------------------------------------------------------------------

def log_event(
    event_type: str,
    username: str = "",
    ip_address: str = "",
    details: dict[str, Any] | str = "",
    user_agent: str = "",
    success: bool = True,
) -> None:
    """Record an audit event to the database and logger.

    Args:
        event_type: One of AuditEvent constants.
        username: The user involved (if applicable).
        ip_address: Client IP address.
        details: Additional context (dict or string).
        user_agent: Browser/client user agent string.
        success: Whether the action was successful.
    """
    timestamp = datetime.utcnow().isoformat() + "Z"
    details_str = json.dumps(details) if isinstance(details, dict) else str(details)

    # Log to Python logger
    log_msg = f"[AUDIT] {event_type} | user={username} | ip={ip_address} | success={success}"
    if success:
        logger.info(log_msg)
    else:
        logger.warning(log_msg)

    # Persist to SQLite
    try:
        init_audit_db()
        with sqlite3.connect(AUDIT_DB_PATH) as conn:
            conn.execute(
                """
                INSERT INTO audit_log (timestamp, event_type, username, ip_address, details, user_agent, success)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (timestamp, event_type, username, ip_address, details_str, user_agent, int(success)),
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to write audit log: {e}")


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------

def log_login_success(username: str, ip_address: str = "") -> None:
    """Record a successful login."""
    log_event(AuditEvent.LOGIN_SUCCESS, username=username, ip_address=ip_address)


def log_login_failed(username: str, ip_address: str = "", reason: str = "") -> None:
    """Record a failed login attempt."""
    log_event(
        AuditEvent.LOGIN_FAILED,
        username=username,
        ip_address=ip_address,
        details={"reason": reason},
        success=False,
    )


def log_signup(username: str, ip_address: str = "", village: str = "") -> None:
    """Record a new account creation."""
    log_event(
        AuditEvent.SIGNUP,
        username=username,
        ip_address=ip_address,
        details={"village": village},
    )


def log_prediction(username: str, crop: str, label: str, confidence: float, ip_address: str = "") -> None:
    """Record a disease prediction request."""
    log_event(
        AuditEvent.PREDICTION_REQUEST,
        username=username,
        ip_address=ip_address,
        details={"crop": crop, "prediction": label, "confidence": round(confidence, 4)},
    )


# ---------------------------------------------------------------------------
# Query functions
# ---------------------------------------------------------------------------

def get_recent_events(
    username: str | None = None,
    event_type: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Query recent audit events with optional filters.

    Args:
        username: Filter by specific user (None for all users).
        event_type: Filter by event type (None for all types).
        limit: Maximum number of records to return.

    Returns:
        List of audit event dicts, newest first.
    """
    init_audit_db()

    query = "SELECT timestamp, event_type, username, ip_address, details, success FROM audit_log"
    conditions = []
    params: list[Any] = []

    if username:
        conditions.append("username = ?")
        params.append(username)
    if event_type:
        conditions.append("event_type = ?")
        params.append(event_type)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    with sqlite3.connect(AUDIT_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, params).fetchall()

    return [dict(row) for row in rows]


def get_failed_login_count(username: str, hours: int = 24) -> int:
    """Count failed login attempts for a user in the last N hours.

    Useful for detecting brute-force attacks and implementing account lockout.
    """
    init_audit_db()

    from datetime import timedelta
    cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat() + "Z"

    with sqlite3.connect(AUDIT_DB_PATH) as conn:
        result = conn.execute(
            """
            SELECT COUNT(*) FROM audit_log
            WHERE username = ? AND event_type = ? AND timestamp > ? AND success = 0
            """,
            (username, AuditEvent.LOGIN_FAILED, cutoff),
        ).fetchone()

    return result[0] if result else 0


def get_user_activity_summary(username: str) -> dict[str, Any]:
    """Get a summary of a user's audit activity.

    Returns:
        Dict with total_events, last_login, failed_attempts_24h, and recent_events.
    """
    init_audit_db()

    with sqlite3.connect(AUDIT_DB_PATH) as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM audit_log WHERE username = ?", (username,)
        ).fetchone()[0]

        last_login = conn.execute(
            "SELECT timestamp FROM audit_log WHERE username = ? AND event_type = ? ORDER BY id DESC LIMIT 1",
            (username, AuditEvent.LOGIN_SUCCESS),
        ).fetchone()

    return {
        "username": username,
        "total_events": total,
        "last_login": last_login[0] if last_login else None,
        "failed_attempts_24h": get_failed_login_count(username, hours=24),
        "recent_events": get_recent_events(username=username, limit=10),
    }
