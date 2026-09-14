"""Input validation utilities for AgriSmart authentication and user management.

Provides password strength checking, username policy enforcement, and
input sanitization for farmer profile fields.
"""

from __future__ import annotations

import re
from typing import Tuple


# ---------------------------------------------------------------------------
# Password strength policy
# ---------------------------------------------------------------------------

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

# Character class patterns
_HAS_UPPER = re.compile(r"[A-Z]")
_HAS_LOWER = re.compile(r"[a-z]")
_HAS_DIGIT = re.compile(r"\d")
_HAS_SPECIAL = re.compile(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?`~]")

# Common weak passwords to reject
WEAK_PASSWORDS = frozenset({
    "password", "12345678", "123456789", "1234567890", "qwerty123",
    "password1", "password123", "admin123", "letmein", "welcome",
    "agrismart", "farmer123", "kisan123", "agriculture",
})


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Validate password against security policy.

    Returns:
        Tuple of (is_valid, message). If invalid, message describes the failure.
    """
    if not password:
        return False, "Password cannot be empty."

    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."

    if len(password) > MAX_PASSWORD_LENGTH:
        return False, f"Password must not exceed {MAX_PASSWORD_LENGTH} characters."

    if password.lower() in WEAK_PASSWORDS:
        return False, "This password is too common. Please choose a stronger password."

    missing = []
    if not _HAS_UPPER.search(password):
        missing.append("uppercase letter")
    if not _HAS_LOWER.search(password):
        missing.append("lowercase letter")
    if not _HAS_DIGIT.search(password):
        missing.append("digit")

    if len(missing) > 1:
        return False, f"Password must contain at least one {', one '.join(missing)}."

    # Calculate strength score
    score = 0
    score += min(len(password), 20) * 2  # Length bonus (up to 40)
    score += 10 if _HAS_UPPER.search(password) else 0
    score += 10 if _HAS_LOWER.search(password) else 0
    score += 15 if _HAS_DIGIT.search(password) else 0
    score += 20 if _HAS_SPECIAL.search(password) else 0

    if score < 30:
        return False, "Password is too weak. Add more variety (uppercase, digits, or symbols)."

    return True, "Password meets security requirements."


def get_password_strength_label(password: str) -> str:
    """Return a human-readable strength label: Weak, Fair, Good, Strong, Excellent."""
    if not password or len(password) < MIN_PASSWORD_LENGTH:
        return "Weak"

    score = 0
    score += min(len(password), 20) * 2
    score += 10 if _HAS_UPPER.search(password) else 0
    score += 10 if _HAS_LOWER.search(password) else 0
    score += 15 if _HAS_DIGIT.search(password) else 0
    score += 20 if _HAS_SPECIAL.search(password) else 0

    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Strong"
    elif score >= 45:
        return "Good"
    elif score >= 30:
        return "Fair"
    return "Weak"


# ---------------------------------------------------------------------------
# Username validation
# ---------------------------------------------------------------------------

MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 30
_VALID_USERNAME = re.compile(r"^[a-zA-Z][a-zA-Z0-9._-]*$")

RESERVED_USERNAMES = frozenset({
    "admin", "root", "system", "agrismart", "api", "support",
    "moderator", "null", "undefined", "test", "demo",
})


def validate_username(username: str) -> Tuple[bool, str]:
    """Validate username against naming policy.

    Rules:
        - 3–30 characters long
        - Must start with a letter
        - Only alphanumeric, dots, hyphens, and underscores
        - Cannot be a reserved system name
    """
    if not username:
        return False, "Username cannot be empty."

    clean = username.strip()

    if len(clean) < MIN_USERNAME_LENGTH:
        return False, f"Username must be at least {MIN_USERNAME_LENGTH} characters."

    if len(clean) > MAX_USERNAME_LENGTH:
        return False, f"Username must not exceed {MAX_USERNAME_LENGTH} characters."

    if clean.lower() in RESERVED_USERNAMES:
        return False, f"'{clean}' is a reserved name. Please choose another username."

    if not _VALID_USERNAME.match(clean):
        return False, "Username must start with a letter and contain only letters, digits, dots, hyphens, or underscores."

    return True, "Username is valid."


# ---------------------------------------------------------------------------
# Profile field sanitization
# ---------------------------------------------------------------------------

def sanitize_village_name(village: str) -> str:
    """Clean and normalize village/city name input."""
    if not village:
        return "Pune"
    cleaned = re.sub(r"[<>\"';{}()\[\]\\]", "", village.strip())
    return cleaned[:100] if cleaned else "Pune"


def sanitize_farmer_name(name: str) -> str:
    """Clean and normalize farmer full name."""
    if not name:
        return ""
    cleaned = re.sub(r"[<>\"';{}()\[\]\\]", "", name.strip())
    return cleaned[:80]


def validate_plot_count(count: int | None) -> int:
    """Ensure plot count is within reasonable bounds (1–500)."""
    if count is None or count < 1:
        return 1
    return min(count, 500)
