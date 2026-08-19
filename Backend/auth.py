# auth.py
# ------------------------------------------------------
# Handles admin login.
#
# How it works:
# 1. Frontend sends the passcode the admin typed to POST /admin/login
# 2. We compare it to ADMIN_PASSCODE (stored here, server-side only —
#    the frontend JavaScript never contains this value, so nobody
#    can find it by viewing page source)
# 3. If correct, we generate a random token and remember it
# 4. The frontend stores that token and sends it with every future
#    admin request. Later (Step 11) we'll check this token before
#    allowing access to /admin/sales, /admin/ingredients, etc.
# ------------------------------------------------------

import secrets
from fastapi import Header, HTTPException


# TODO: change this to your own passcode.
# Later, move this into an environment variable instead of hardcoding it
# here, so it's not sitting in your source code at all. For now, as
# beginners, keeping it in this one backend-only file is fine —
# the key rule is: this value must NEVER appear in any frontend file.
ADMIN_PASSCODE = "coffee1234"

# Keeps track of which tokens are currently "logged in".
# This is just a Python set living in memory — it resets to empty
# every time the server restarts. That's fine for a beginner project;
# it just means admins need to log in again after a server restart.
active_tokens = set()


def check_passcode(passcode: str) -> bool:
    """Returns True if the given passcode matches the admin passcode."""
    return passcode == ADMIN_PASSCODE


def create_token() -> str:
    """Generates a new random, hard-to-guess token and remembers it."""
    token = secrets.token_hex(16)  # e.g. "a3f9c1e2b8d7..."
    active_tokens.add(token)
    return token


def is_valid_token(token: str) -> bool:
    """Checks whether a given token is currently logged in."""
    return token in active_tokens


def get_current_admin(
    x_admin_token: str | None = Header(default=None)
) -> str:
    """Checks whether the request contains a valid admin token."""

    if not x_admin_token:
        raise HTTPException(
            status_code=401,
            detail="Admin login required"
        )

    if not is_valid_token(x_admin_token):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return "admin"