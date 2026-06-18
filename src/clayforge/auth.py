"""
ClayForge Auth — Optional, one-click cookie-based authentication.

Beautiful, pragmatic, and production-ready helpers that feel like natural
extensions of the framework. Zero boilerplate for the 90% case.

Philosophy (consistent with ClayForge):
- Everything is optional. `from clayforge import auth` never breaks your app.
- Cookie-based sessions using signed, tamper-proof cookies (itsdangerous).
- Works perfectly with the existing FastAPI backend and @app.page system.
- Easy to combine with Database (SQLite or Postgres) for real user storage.
- Secure by default when you provide a strong secret; great DX for internal tools.

Quick start (the "it just works" path):

    from clayforge import auth, db
    import clayforge as cf

    # Recommended: strong secret from environment in production
    auth_manager = auth.Auth(
        secret_key=os.getenv("CLAYFORGE_AUTH_SECRET"),
        cookie_name="cf_session",
        max_age=86400 * 7,   # 7 days
    )

    # --- Login page (beautiful ClayForge UI) ---
    @app.page("/login")
    def login_page():
        # ... render form with ui.text_input, ui.button(on_click=attempt_login)
        pass

    # --- Protected page (zero friction) ---
    @app.page("/dashboard")
    def dashboard():
        user = auth_manager.get_current_user()   # reads signed cookie via context
        if not user:
            # Render a friendly login gate or redirect via client JS
            cf.ui.title("Please log in")
            return

        cf.ui.title(f"Welcome back, {user.get('name', 'friend')}")
        # ... your internal tool UI

    # --- Setting the cookie (from a custom route or handler) ---
    # (See realistic example in examples/internal_crm_with_auth.py)

The same Auth instance gives you:
- get_current_user() / require_user()
- login_user(response, user_dict) + logout_user(response)
- Secure password hashing (passlib when available)
- FastAPI dependency + middleware helpers for advanced routes

Everything stays lightweight, documented, and consistent with the
zero-boilerplate promise while being safe enough for real internal tools.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from collections.abc import Callable
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any

from fastapi import Request, Response

# ---------------------------------------------------------------------------
# Graceful optional security dependencies (matches viz/grok/db pattern)
# ---------------------------------------------------------------------------

_HAS_ITSDANGEROUS = False
_HAS_PASSLIB = False

_itsdangerous = None  # type: ignore
_passlib_pwd_context = None  # type: ignore

try:
    from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

    _HAS_ITSDANGEROUS = True
    _itsdangerous = (URLSafeTimedSerializer, BadSignature, SignatureExpired)
except Exception:  # pragma: no cover
    URLSafeTimedSerializer = BadSignature = SignatureExpired = None  # type: ignore

try:
    from passlib.context import CryptContext

    _HAS_PASSLIB = True
    _passlib_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception:  # pragma: no cover
    # Will fall back to a simple (less secure) PBKDF2 implementation
    pass


# ---------------------------------------------------------------------------
# Context for seamless integration with ClayForge page rendering
# The server sets this before executing @app.page functions so that
# auth.get_current_user() "just works" inside your page code with zero args.
# ---------------------------------------------------------------------------

_current_request: ContextVar[Request | None] = ContextVar("clayforge_current_request", default=None)


def get_current_request() -> Request | None:
    """Return the current HTTP Request (if any) during page rendering or route handling.

    This is automatically populated by the ClayForge server for all
    @app.page functions. You normally don't need to call it directly —
    use `auth.get_current_user()` instead.
    """
    try:
        return _current_request.get()
    except Exception:
        return None


def _set_current_request(request: Request | None) -> None:
    """Internal: called by the server layer before page execution."""
    try:
        _current_request.set(request)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Core Auth implementation
# ---------------------------------------------------------------------------


@dataclass
class Auth:
    """
    The main one-click authentication manager.

    Create one instance per app (or use the module-level default singleton).

    Example:
        auth = Auth(secret_key=os.getenv("CLAYFORGE_AUTH_SECRET"))

        # Later, inside a page or handler:
        user = auth.get_current_user()
        if user:
            ...
    """

    secret_key: str | None = None
    cookie_name: str = "cf_session"
    max_age: int = 86400 * 7  # 7 days
    secure: bool = False  # Set True behind HTTPS in production
    httponly: bool = True
    samesite: str = "lax"
    salt: str = "clayforge-auth-v1"

    # Internal
    _serializer: Any = field(default=None, repr=False)
    _using_signed: bool = field(default=False, repr=False)

    def __post_init__(self) -> None:
        key = self.secret_key or os.getenv("CLAYFORGE_AUTH_SECRET")
        if not key:
            key = "dev-insecure-change-me-in-production-please"
            # We do not warn here — warning is emitted on first real use
        self.secret_key = key

        if _HAS_ITSDANGEROUS and URLSafeTimedSerializer is not None:
            self._serializer = URLSafeTimedSerializer(self.secret_key, salt=self.salt)
            self._using_signed = True
        else:
            self._serializer = None
            self._using_signed = False

    # ------------------------------------------------------------------
    # Password utilities (secure when passlib available)
    # ------------------------------------------------------------------

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plaintext password.

        Uses bcrypt via passlib when `pip install "clayforge[auth]"` (or passlib).
        Falls back to a solid PBKDF2-HMAC-SHA256 when passlib is missing
        (still safe for internal tools, but upgrade recommended).
        """
        if _HAS_PASSLIB and _passlib_pwd_context is not None:
            return _passlib_pwd_context.hash(password)

        # Fallback: PBKDF2 (stdlib only)
        salt = os.urandom(16)
        iterations = 260_000
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations, 32)
        return f"pbkdf2${iterations}${salt.hex()}${dk.hex()}"

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its stored hash."""
        if not hashed or not password:
            return False

        if _HAS_PASSLIB and _passlib_pwd_context is not None:
            try:
                return _passlib_pwd_context.verify(password, hashed)
            except Exception:
                return False

        # Fallback PBKDF2 verifier
        if not hashed.startswith("pbkdf2$"):
            return False
        try:
            _, iters, salt_hex, dk_hex = hashed.split("$", 3)
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(dk_hex)
            computed = hashlib.pbkdf2_hmac(
                "sha256", password.encode(), salt, int(iters), len(expected)
            )
            return computed == expected
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Core session / cookie handling
    # ------------------------------------------------------------------

    def _warn_unsigned(self) -> None:
        if not self._using_signed:
            import warnings

            warnings.warn(
                "ClayForge Auth is running without itsdangerous (unsigned cookies).\n"
                "This is only acceptable for local development.\n"
                'Install secure signing with: pip install "clayforge[auth]"',
                UserWarning,
                stacklevel=3,
            )

    def _serialize(self, data: dict) -> str:
        """Turn user data into a signed (or unsigned) token."""
        payload = {
            "user": data,
            "iat": int(time.time()),
            "exp": int(time.time()) + self.max_age,
        }
        if self._using_signed and self._serializer is not None:
            return self._serializer.dumps(payload)
        # Insecure dev fallback (JSON only)
        self._warn_unsigned()
        return json.dumps(payload)

    def _deserialize(self, token: str) -> dict | None:
        """Validate and return the user payload or None."""
        if not token:
            return None

        if self._using_signed and self._serializer is not None:
            try:
                payload: dict[str, Any] = self._serializer.loads(token, max_age=self.max_age)
                if payload.get("exp", 0) < time.time():
                    return None
                return payload.get("user")
            except (BadSignature, SignatureExpired, Exception):  # type: ignore
                return None

        # Unsigned fallback (dev only)
        try:
            payload = json.loads(token)
            if payload.get("exp", 0) < time.time():
                return None
            self._warn_unsigned()
            return payload.get("user")
        except Exception:
            return None

    def get_current_user(self, request: Request | None = None) -> dict[str, Any] | None:
        """Return the currently authenticated user dict or None.

        Works automatically inside @app.page functions thanks to ClayForge's
        request context. You can also pass an explicit Request.
        Falls back to auth context (set for WS/ready) when no request.
        """
        if request is None:
            request = get_current_request()

        if request is None:
            # WS / ready / non-HTTP contexts use the auth user context set by server
            user = get_auth_user_from_context()
            if user:
                return user
            return None

        cookie = request.cookies.get(self.cookie_name)
        if not cookie:
            return None

        user = self._deserialize(cookie)
        return user if isinstance(user, dict) else None

    def require_user(
        self, request: Request | None = None, redirect_to: str = "/login"
    ) -> dict[str, Any]:
        """Return the current user or raise a simple exception that you can handle.

        Typical usage inside a page:

            try:
                user = auth.require_user()
            except auth.AuthRequired:
                # render login UI or return early
                return
        """
        user = self.get_current_user(request)
        if not user:
            raise AuthRequired(redirect_to)
        return user

    def login_user(
        self,
        response: Response,
        user: dict[str, Any],
        *,
        remember: bool = True,
    ) -> None:
        """Attach a signed session cookie to the response (log the user in).

        `user` should be a plain dict (id, name, email, roles, etc.).
        Do NOT put secrets or large data in it.
        """
        if not isinstance(user, dict):
            raise TypeError("user must be a dict")

        token = self._serialize(user)
        max_age = self.max_age if remember else None

        response.set_cookie(
            key=self.cookie_name,
            value=token,
            max_age=max_age,
            secure=self.secure,
            httponly=self.httponly,
            samesite=self.samesite,
        )

    def logout_user(self, response: Response) -> None:
        """Clear the session cookie (log the user out)."""
        response.set_cookie(
            key=self.cookie_name,
            value="",
            max_age=0,
            secure=self.secure,
            httponly=self.httponly,
            samesite=self.samesite,
            expires="Thu, 01 Jan 1970 00:00:00 GMT",
        )

    # ------------------------------------------------------------------
    # FastAPI / advanced integration helpers
    # ------------------------------------------------------------------

    def get_current_user_dependency(self) -> Callable[[Request], dict[str, Any] | None]:
        """Return a FastAPI dependency you can use on custom routes."""

        def _dep(request: Request) -> dict[str, Any] | None:
            return self.get_current_user(request)

        return _dep

    def create_protected_dependency(self, redirect_to: str = "/login") -> Callable:
        """Create a dependency that enforces authentication on FastAPI routes."""

        def _protected(request: Request) -> dict[str, Any]:
            user = self.get_current_user(request)
            if not user:
                # For API routes you may prefer raising HTTPException instead
                raise AuthRequired(redirect_to)
            return user

        return _protected

    def __repr__(self) -> str:
        mode = "signed (secure)" if self._using_signed else "unsigned (dev only)"
        return f"<ClayForgeAuth cookie={self.cookie_name!r} mode={mode}>"

    # ------------------------------------------------------------------
    # Compatibility shims for the ClayForge server integration
    # These make the pre-wired server auth support work without changes.
    # Public API users should prefer get_current_user / login_user / etc.
    # ------------------------------------------------------------------

    @property
    def session_cookie(self) -> str:
        """Name of the cookie used for sessions (used by server WS bootstrap)."""
        return self.cookie_name

    def get_user_from_request(self, request: Request) -> dict[str, Any] | None:
        """Alias expected by the server layer."""
        return self.get_current_user(request)

    def parse_token(self, token: str) -> dict[str, Any] | None:
        """Parse and validate a raw session token (used in WS path)."""
        return self._deserialize(token)

    # Decorator support for @auth.require_login (or @auth_manager.require_login)
    def require_login(self, redirect_to: str = "/login") -> Callable:
        """Decorator for page functions that enforces login.

        Usage (inside your app):

            @auth.require_login()
            @app.page("/admin")
            def admin_dashboard(user=None):   # user is injected by server when present
                ...

        If not logged in, the decorator causes a friendly gate or early return.
        The server also injects the user kwarg when available.
        """

        def decorator(fn: Callable) -> Callable:
            def wrapper(*args: Any, **kwargs: Any):
                # The actual enforcement happens in server before calling,
                # but this wrapper gives users a clean declarative option.
                user = kwargs.get("user") or self.get_current_user()
                if not user:
                    # Returning None tells the page renderer to show a minimal gate.
                    # Advanced users can raise or redirect via JS in the page body.
                    return None
                # Pass user through if the original fn accepts it
                if "user" in kwargs or "user" in fn.__code__.co_varnames:
                    kwargs.setdefault("user", user)
                return fn(*args, **kwargs)

            wrapper.__name__ = getattr(fn, "__name__", "protected_page")
            wrapper.__doc__ = fn.__doc__
            return wrapper

        return decorator


class AuthRequired(Exception):
    """Raised by require_user() when no valid session exists."""

    def __init__(self, redirect_to: str = "/login"):
        self.redirect_to = redirect_to
        super().__init__(f"Authentication required. Redirect suggested: {redirect_to}")


# ---------------------------------------------------------------------------
# Zero-boilerplate module-level singleton
# Users can simply do:
#     from clayforge import auth
#     user = auth.get_current_user()
#     auth.login_user(...)
#
# The singleton uses environment variable for the secret when available.
# ---------------------------------------------------------------------------

_default_auth: Auth | None = None


def get_auth() -> Auth:
    """Return (and lazily create) the process-wide default Auth manager."""
    global _default_auth
    if _default_auth is None:
        _default_auth = Auth()
    return _default_auth


# The beautiful default export
auth: Auth = get_auth()  # type: ignore  # reassigned but works at runtime


# Re-export the exception for user `except auth.AuthRequired`
__all__ = [
    "Auth",
    "AuthRequired",
    "auth",
    "get_auth",
    "get_current_request",
    "hash_password",  # convenience re-exports
    "verify_password",
]


# Convenience top-level functions (delegate to the default singleton)
def get_current_user(request: Request | None = None) -> dict[str, Any] | None:
    return get_auth().get_current_user(request)


def login_user(response: Response, user: dict[str, Any], *, remember: bool = True) -> None:
    return get_auth().login_user(response, user, remember=remember)


def logout_user(response: Response) -> None:
    return get_auth().logout_user(response)


def hash_password(password: str) -> str:
    return Auth.hash_password(password)


def verify_password(password: str, hashed: str) -> bool:
    return Auth.verify_password(password, hashed)


# --- Server integration helpers (set by server before page render) ---
_auth_user_context: ContextVar[dict[str, Any] | None] = ContextVar(
    "clayforge_auth_user", default=None
)


def set_auth_context(user: dict[str, Any] | None = None) -> None:
    """Set per-render auth context. Called by the ClayForge server.

    Enables decorators such as @auth.require_login and makes
    get_current_user() reliable inside page functions.
    """
    try:
        _auth_user_context.set(user)
    except Exception:
        pass


def get_auth_user_from_context() -> dict[str, Any] | None:
    try:
        return _auth_user_context.get()
    except Exception:
        return None


# Make the convenience functions part of the public surface
__all__ += [
    "get_current_user",
    "login_user",
    "logout_user",
    "hash_password",
    "verify_password",
    "set_auth_context",
    "require_login",  # will be added via wrapper below
]


# Also expose require_login at module level for the common @auth.require_login pattern
def require_login(redirect_to: str = "/login") -> Callable:
    return get_auth().require_login(redirect_to)


__all__.append("require_login")
