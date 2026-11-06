"""The checks test the real goal, not the shape of one answer. Each wrong fix below is one people
really try: it makes the symptom go away, or looks right, and the check must still fail it. Each
other fix is a different, valid answer, and the check must pass it.

A fix is a list of (old, new) edits applied to the case as shipped ("case") or to its solution
("solution"). Every old string must appear exactly once, so a fix cannot silently stop applying.
"""

import types
from pathlib import Path

import pytest

from trust.__main__ import CASES
from trust.checks import CHECKS

ROOT = Path(__file__).resolve().parent.parent

Edit = tuple[str, str]

WRONG: dict[str, tuple[int, str, list[Edit]]] = {
    "01 strip the quotes out of the inputs": (
        1,
        "case",
        [
            (
                '            email = request.form.get("email", "")\n'
                '            password = request.form.get("password", "")\n',
                '            email = request.form.get("email", "").replace("\'", "")\n'
                '            password = request.form.get("password", "").replace("\'", "")\n',
            )
        ],
    ),
    "02 delete the literal <script> tag": (
        2,
        "case",
        [
            (
                'f"<p>You searched for: {term}</p>"',
                'f"<p>You searched for: {term.replace(chr(60) + chr(115) + chr(99) + chr(114) + chr(105) + chr(112) + chr(116) + chr(62), chr(0))}</p>"',
            )
        ],
    ),
    "03 strip <script> from the stored body": (
        3,
        "case",
        [
            (
                'f"<li><b>{author}</b>: {body}</li>"',
                'f"<li><b>{author}</b>: {body.replace(chr(60) + chr(115) + chr(99) + chr(114) + chr(105) + chr(112) + chr(116) + chr(62), chr(32))}</li>"',
            )
        ],
    ),
    "04 special-case the one invoice that leaked": (
        4,
        "case",
        [
            (
                "            owner, amount_cents, memo = row\n",
                '            if invoice_id == "inv_5002":\n'
                '                return Response(404, {"error": "no such invoice"})\n'
                "            owner, amount_cents, memo = row\n",
            )
        ],
    ),
    "05 trust an X-Role header the client sends": (
        5,
        "case",
        [
            (
                '            if session is None:\n                return Response(401, {"error": "sign in"})\n',
                '            if session is None:\n                return Response(401, {"error": "sign in"})\n'
                '            if request.headers.get("x-role") != "admin" and session.role != "admin":\n'
                '                return Response(403, {"error": "forbidden"})\n',
            )
        ],
    ),
    "06 accept any non-empty token": (
        6,
        "case",
        [
            (
                '            email_of[session.user] = request.form.get("new_email", "")\n',
                '            if not request.form.get("csrf"):\n'
                '                return Response(403, {"error": "missing csrf token"})\n'
                '            email_of[session.user] = request.form.get("new_email", "")\n',
            )
        ],
    ),
    "07 blocklist only the role field": (
        7,
        "case",
        [
            (
                "            for column, value in body.items():\n                db.execute(",
                "            for column, value in body.items():\n"
                '                if column == "role":\n'
                "                    continue\n"
                "                db.execute(",
            )
        ],
    ),
    "08 blocklist only the metadata IP": (
        8,
        "case",
        [
            (
                '    if host not in resolver:\n        return 0, "could not resolve host"\n',
                '    if host == "169.254.169.254":\n        return 0, "host not allowed"\n'
                '    if host not in resolver:\n        return 0, "could not resolve host"\n',
            )
        ],
    ),
    "09 reject names that contain ..": (
        9,
        "case",
        [
            (
                "            full = os.path.join(base, name)\n            try:\n",
                '            if ".." in name:\n                return Response(404, {"error": "no such file"})\n'
                "            full = os.path.join(base, name)\n            try:\n",
            )
        ],
    ),
    "10 block only values that start with http": (
        10,
        "case",
        [
            (
                '            target = request.query.get("next", "/")\n'
                "            # The bug: the next value is used as the redirect target as-is. It can name any site.\n",
                '            target = request.query.get("next", "/")\n'
                '            if target.startswith("http"):\n                target = "/"\n',
            )
        ],
    ),
}

RIGHT: dict[str, tuple[int, str, list[Edit]]] = {
    "01 escape by doubling the quotes": (
        1,
        "case",
        [
            (
                "            query = (\n"
                "                f\"SELECT id, role FROM users WHERE email = '{email}' AND password = '{password}'\"\n"
                "            )\n"
                "            row = db.execute(query).fetchone()\n",
                '            safe_email = email.replace("\'", "\'\'")\n'
                '            safe_password = password.replace("\'", "\'\'")\n'
                "            query = (\n"
                "                f\"SELECT id, role FROM users WHERE email = '{safe_email}' AND password = '{safe_password}'\"\n"
                "            )\n"
                "            row = db.execute(query).fetchone()\n",
            )
        ],
    ),
    "02 escape the angle brackets by hand": (
        2,
        "case",
        [
            (
                'f"<p>You searched for: {term}</p>"',
                'f"<p>You searched for: {term.replace(chr(38), chr(38) + chr(97) + chr(109) + chr(112) + chr(59)).replace(chr(60), chr(38) + chr(108) + chr(116) + chr(59)).replace(chr(62), chr(38) + chr(103) + chr(116) + chr(59))}</p>"',
            )
        ],
    ),
    "06 compare the token in constant time": (
        6,
        "case",
        [
            (
                '            email_of[session.user] = request.form.get("new_email", "")\n',
                "            import hmac\n"
                '            if not hmac.compare_digest(request.form.get("csrf", ""), session.csrf):\n'
                '                return Response(403, {"error": "bad or missing csrf token"})\n'
                '            email_of[session.user] = request.form.get("new_email", "")\n',
            )
        ],
    ),
    "07 allow only the fields a profile edit may change": (
        7,
        "case",
        [
            (
                "            for column, value in body.items():\n"
                '                db.execute(f"UPDATE users SET {column} = ? WHERE id = ?", (value, session.user))\n',
                '            allowed = ("display_name", "email")\n'
                "            for column, value in body.items():\n"
                "                if column in allowed:\n"
                '                    db.execute(f"UPDATE users SET {column} = ? WHERE id = ?", (value, session.user))\n',
            )
        ],
    ),
    "08 allow only the avatar host": (
        8,
        "case",
        [
            (
                '    if host not in resolver:\n        return 0, "could not resolve host"\n',
                '    if host not in frozenset({"images.acme.test"}):\n        return 0, "host not allowed"\n'
                '    if host not in resolver:\n        return 0, "could not resolve host"\n',
            )
        ],
    ),
    "09 confine the path with commonpath": (
        9,
        "case",
        [
            (
                "            full = os.path.join(base, name)\n            try:\n",
                "            full = os.path.realpath(os.path.join(base, name))\n"
                "            if os.path.commonpath([os.path.realpath(base), full]) != os.path.realpath(base):\n"
                '                return Response(404, {"error": "no such file"})\n'
                "            try:\n",
            )
        ],
    ),
}


def load(number: int, source: str, edits: list[Edit]) -> types.ModuleType:
    name = CASES[number][0]
    path = ROOT / ("cases" if source == "case" else "tests/solutions") / f"{name}.py"
    text = path.read_text()
    for old, new in edits:
        assert text.count(old) == 1, f"edit does not apply: {old!r}"
        text = text.replace(old, new)
    module = types.ModuleType(f"variant_{name}")
    module.__dict__["__file__"] = str(path)
    exec(compile(text, str(path), "exec"), module.__dict__)  # noqa: S102
    return module


@pytest.mark.parametrize("name", list(WRONG))
def test_check_rejects_a_wrong_fix(name):
    number, source, edits = WRONG[name]

    results = CHECKS[number](load(number, source, edits))

    assert not all(ok for _, ok in results), results


@pytest.mark.parametrize("name", list(RIGHT))
def test_check_accepts_another_real_fix(name):
    number, source, edits = RIGHT[name]

    results = CHECKS[number](load(number, source, edits))

    assert all(ok for _, ok in results), results
