"""Session token management with expiry for AgriSmart authentication.

Provides secure token generation, validation, and expiry tracking
for stateless API session management. Tokens are stored in-memory
with automatic cleanup of expired sessions.
"""

from __future__ import annotations

import hashlib
import os
import time
from dataclasses import dataclass, field
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Session data model
# ---------------------------------------------------------------------------

@dataclass
class Session:
    """Represents an active user session."""
    token: str
    username: str
    user_data: dict[str, Any]
    created_at: float
    expires_at: float
    last_activity: float
    ip_address: str = ""

    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    @property
    def remaining_seconds(self) -> float:
        return max(0, self.expires_at - time.time())

    def refresh(self, extension_seconds: int = 3600) -> None:
        """Extend session expiry from current time."""
        self.last_activity = time.time()
        self.expires_at = self.last_activity + extension_seconds


# ---------------------------------------------------------------------------
# Session Store
# ---------------------------------------------------------------------------

class SessionStore:
    """In-memory session store with automatic expiry cleanup.

    Args:
        default_ttl: Default session lifetime in seconds (default 24 hours).
        max_sessions_per_user: Maximum concurrent sessions per username.
        cleanup_interval: Minimum seconds between automatic cleanups.
    """

    def __init__(
        self,
        default_ttl: int = 86400,
        max_sessions_per_user: int = 5,
        cleanup_interval: int = 300,
    ):
        self._sessions: dict[str, Session] = {}
        self._user_sessions: dict[str, list[str]] = {}
        self.default_ttl = default_ttl
        self.max_sessions_per_user = max_sessions_per_user
        self.cleanup_interval = cleanup_interval
        self._last_cleanup = 0.0

    def _generate_token(self) -> str:
        """Generate a cryptographically secure session token."""
        random_bytes = os.urandom(32)
        timestamp = str(time.time()).encode()
        return hashlib.sha256(random_bytes + timestamp).hexdigest()

    def _maybe_cleanup(self) -> None:
        """Remove expired sessions if cleanup interval has elapsed."""
        now = time.time()
        if now - self._last_cleanup < self.cleanup_interval:
            return

        expired_tokens = [
            token for token, session in self._sessions.items()
            if session.is_expired
        ]

        for token in expired_tokens:
            self._remove_session(token)

        self._last_cleanup = now

    def _remove_session(self, token: str) -> None:
        """Remove a session by token."""
        session = self._sessions.pop(token, None)
        if session and session.username in self._user_sessions:
            user_tokens = self._user_sessions[session.username]
            if token in user_tokens:
                user_tokens.remove(token)
            if not user_tokens:
                del self._user_sessions[session.username]

    def create_session(
        self,
        username: str,
        user_data: dict[str, Any],
        ttl: int | None = None,
        ip_address: str = "",
    ) -> str:
        """Create a new session for a user.

        Args:
            username: The authenticated username.
            user_data: User profile data to store in the session.
            ttl: Session lifetime in seconds (uses default if None).
            ip_address: Client IP address for audit logging.

        Returns:
            The generated session token string.
        """
        self._maybe_cleanup()

        # Enforce max sessions per user
        if username in self._user_sessions:
            while len(self._user_sessions[username]) >= self.max_sessions_per_user:
                oldest_token = self._user_sessions[username][0]
                self._remove_session(oldest_token)

        token = self._generate_token()
        now = time.time()
        session = Session(
            token=token,
            username=username,
            user_data=user_data,
            created_at=now,
            expires_at=now + (ttl or self.default_ttl),
            last_activity=now,
            ip_address=ip_address,
        )

        self._sessions[token] = session

        if username not in self._user_sessions:
            self._user_sessions[username] = []
        self._user_sessions[username].append(token)

        return token

    def validate_session(self, token: str) -> Optional[Session]:
        """Validate a session token and return session data if valid.

        Returns:
            Session object if valid and not expired, None otherwise.
        """
        self._maybe_cleanup()

        session = self._sessions.get(token)
        if session is None:
            return None

        if session.is_expired:
            self._remove_session(token)
            return None

        # Update last activity timestamp
        session.last_activity = time.time()
        return session

    def revoke_session(self, token: str) -> bool:
        """Revoke (logout) a specific session.

        Returns:
            True if session was found and revoked, False if not found.
        """
        if token in self._sessions:
            self._remove_session(token)
            return True
        return False

    def revoke_all_user_sessions(self, username: str) -> int:
        """Revoke all sessions for a specific user (e.g., password change).

        Returns:
            Number of sessions revoked.
        """
        tokens = list(self._user_sessions.get(username, []))
        for token in tokens:
            self._remove_session(token)
        return len(tokens)

    def get_active_sessions_count(self, username: str | None = None) -> int:
        """Get count of active (non-expired) sessions.

        Args:
            username: If provided, count only this user's sessions.
        """
        self._maybe_cleanup()

        if username:
            return len(self._user_sessions.get(username, []))
        return len(self._sessions)

    @property
    def total_active_sessions(self) -> int:
        """Total number of active sessions across all users."""
        self._maybe_cleanup()
        return len(self._sessions)


# ---------------------------------------------------------------------------
# Module-level singleton for convenience
# ---------------------------------------------------------------------------

_default_store: SessionStore | None = None


def get_session_store() -> SessionStore:
    """Get or create the default session store singleton."""
    global _default_store
    if _default_store is None:
        _default_store = SessionStore()
    return _default_store
