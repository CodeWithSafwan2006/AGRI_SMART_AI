"""Authentication & user management for AgriSmart with SQLite storage."""

from __future__ import annotations

import hashlib
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

DB_DIR = Path(__file__).resolve().parents[1] / "data"
DB_PATH = DB_DIR / "users.db"


def init_auth_db() -> None:
    """Initialize SQLite users table with detailed farmer profile columns."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                full_name TEXT,
                village_city TEXT,
                latitude REAL,
                longitude REAL,
                number_of_plots INTEGER DEFAULT 1,
                primary_crop TEXT DEFAULT 'Tomato',
                secondary_crop TEXT DEFAULT 'Corn',
                soil_type TEXT DEFAULT 'Loamy',
                language TEXT DEFAULT 'English',
                created_at TEXT NOT NULL
            )
            """
        )
        # Migrate table columns if existing db lacks new columns
        cursor.execute("PRAGMA table_info(users)")
        existing_cols = {row[1] for row in cursor.fetchall()}
        if "number_of_plots" not in existing_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN number_of_plots INTEGER DEFAULT 1")
        if "primary_crop" not in existing_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN primary_crop TEXT DEFAULT 'Tomato'")
        if "secondary_crop" not in existing_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN secondary_crop TEXT DEFAULT 'Corn'")
        if "soil_type" not in existing_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN soil_type TEXT DEFAULT 'Loamy'")

        conn.commit()


def hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    """Hash a password with PBKDF2 HMAC-SHA256 and unique salt."""
    if salt is None:
        salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100_000,
    )
    return pw_hash.hex(), salt.hex()


def create_user(
    username: str,
    password: str,
    full_name: str = "",
    village_city: str = "Pune",
    latitude: float | None = 18.5204,
    longitude: float | None = 73.8567,
    number_of_plots: int = 1,
    primary_crop: str = "Tomato",
    secondary_crop: str = "Corn",
    soil_type: str = "Loamy",
    language: str = "English",
    crop_preference: Optional[str] = None,
) -> tuple[bool, str]:
    """Register a new user in the database."""
    init_auth_db()
    actual_primary = crop_preference or primary_crop or "Tomato"
    clean_username = username.strip().lower()
    if not clean_username:
        return False, "Username cannot be empty."
    if len(password) < 4:
        return False, "Password must be at least 4 characters long."

    pw_hash, salt_hex = hash_password(password)
    created_at = datetime.utcnow().isoformat()

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (
                    username, password_hash, salt, full_name,
                    village_city, latitude, longitude,
                    number_of_plots, primary_crop, secondary_crop, soil_type,
                    language, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    clean_username,
                    pw_hash,
                    salt_hex,
                    full_name.strip() or clean_username.title(),
                    village_city.strip() or "Pune",
                    latitude,
                    longitude,
                    number_of_plots or 1,
                    actual_primary,
                    secondary_crop or "Corn",
                    soil_type or "Loamy",
                    language or "English",
                    created_at,
                ),
            )
            conn.commit()
            return True, f"Account '{clean_username}' registered successfully!"
    except sqlite3.IntegrityError:
        return False, f"Username '{clean_username}' is already taken. Please choose another."
    except Exception as exc:
        return False, f"Error creating user: {exc}"


def verify_user(username: str, password: str) -> tuple[bool, dict[str, Any] | None, str]:
    """Verify user credentials and return user profile if successful."""
    init_auth_db()
    clean_username = username.strip().lower()
    if not clean_username or not password:
        return False, None, "Please enter both username and password."

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = ?",
                (clean_username,),
            )
            row = cursor.fetchone()
            if not row:
                return False, None, "User not found. Please check username or sign up."

            stored_hash = row["password_hash"]
            salt = bytes.fromhex(row["salt"])
            computed_hash, _ = hash_password(password, salt=salt)

            if computed_hash == stored_hash:
                prim_crop = row["primary_crop"] if "primary_crop" in row.keys() else (row["crop_preference"] if "crop_preference" in row.keys() else "Tomato")
                user_dict = {
                    "id": row["id"],
                    "username": row["username"],
                    "full_name": row["full_name"],
                    "village_city": row["village_city"],
                    "latitude": row["latitude"],
                    "longitude": row["longitude"],
                    "number_of_plots": row["number_of_plots"] if "number_of_plots" in row.keys() else 1,
                    "primary_crop": prim_crop,
                    "crop_preference": prim_crop,
                    "secondary_crop": row["secondary_crop"] if "secondary_crop" in row.keys() else "Corn",
                    "soil_type": row["soil_type"] if "soil_type" in row.keys() else "Loamy",
                    "language": row["language"],
                }
                return True, user_dict, "Login verified successfully!"
            else:
                return False, None, "Incorrect password. Please try again."
    except Exception as exc:
        return False, None, f"Database error during verification: {exc}"


def update_user_location(
    username: str,
    village_city: str,
    latitude: float,
    longitude: float,
) -> tuple[bool, str]:
    """Update a user's location and GPS coordinates in the database."""
    init_auth_db()
    clean_username = username.strip().lower()
    if not clean_username:
        return False, "Username required."

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE users
                SET village_city = ?, latitude = ?, longitude = ?
                WHERE username = ?
                """,
                (village_city.strip(), latitude, longitude, clean_username),
            )
            conn.commit()
            if cursor.rowcount > 0:
                return True, "Location updated successfully."
            return False, "User not found."
    except Exception as exc:
        return False, f"Database update error: {exc}"
