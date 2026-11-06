"""A minimal, correct session store for the cases that need a signed-in user.

It is deliberately not where any bug lives. sign_in checks the password and issues a random
session id; the browser gets it in a cookie. Each session also carries a per-session CSRF token,
which case 06 uses. The cookie is named `sid`.
"""

import secrets
from dataclasses import dataclass

from trust.store import PEOPLE

COOKIE = "sid"
_PASSWORDS = {email: password for _, email, _, _, password, _ in PEOPLE}
_USER_BY_EMAIL = {email: uid for uid, email, *_ in PEOPLE}


@dataclass
class Session:
    user: str
    role: str
    csrf: str


class Sessions:
    def __init__(self) -> None:
        self.by_id: dict[str, Session] = {}

    def sign_in(self, email: str, password: str, role: str) -> str | None:
        if _PASSWORDS.get(email) != password:
            return None
        sid = secrets.token_urlsafe(24)
        self.by_id[sid] = Session(
            user=_USER_BY_EMAIL[email], role=role, csrf=secrets.token_urlsafe(24)
        )
        return sid

    def of(self, sid: str | None) -> Session | None:
        return self.by_id.get(sid or "")

    def cookie(self, sid: str) -> str:
        return f"{COOKIE}={sid}; Path=/; HttpOnly; SameSite=Lax"
