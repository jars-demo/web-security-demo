"""How each case is checked, over real sockets on 127.0.0.1. Every check takes the case module,
so the tests can check a fixed copy too.

Each check proves the feature still works as well as that the weakness is gone, so turning the
feature off is never a fix. A FAIL line names exactly what went wrong.
"""

from collections.abc import Callable
from types import ModuleType

from trust.http import Client, serve

Check = tuple[str, bool]


def attempt(fn: Callable[[], object]) -> object:
    try:
        return fn()
    except Exception as error:  # a crash is an answer too
        return error


def check_01(m: ModuleType) -> list[Check]:
    with serve(m.build()) as port:

        def login(email: str, password: str):
            return Client(port).post("/login", form={"email": email, "password": password})

        good = login("u_1041@acme.test", "hunter2-correct")
        quoted = login("u_1042@acme.test", "let's-go-42")
        wrong = login("u_1041@acme.test", "nope")
        or_true = login("x' OR '1'='1' -- ", "anything")
        as_admin = login("u_1099@acme.test' -- ", "anything")

    return [
        (
            f"u_1041 signs in with the right password (got {good.status})",
            good.status == 200 and good.json.get("user") == "u_1041",
        ),
        (
            f"u_1042 signs in with a password that has a quote (got {quoted.status})",
            quoted.status == 200 and quoted.json.get("user") == "u_1042",
        ),
        (f"a wrong password is refused (got {wrong.status})", wrong.status == 401),
        (
            f"the OR-always-true email does not sign anyone in (got {or_true.status})",
            or_true.status == 401,
        ),
        (
            f"a comment payload does not sign in as the admin (got {as_admin.status})",
            as_admin.status == 401,
        ),
    ]


def check_02(m: ModuleType) -> list[Check]:
    with serve(m.build()) as port:
        client = Client(port)
        plain = client.get("/search?q=revenue").text
        script = client.get(
            "/search?q=%3Cscript%3Efetch('/x?c='%2Bdocument.cookie)%3C/script%3E"
        ).text
        attr = client.get("/search?q=%22%3E%3Cimg%20src%3Dx%20onerror%3Dalert(1)%3E").text

    return [
        ("a plain search term still shows in the page", "revenue" in plain),
        ("a matching document is still listed", "Q3 revenue memo" in plain),
        ("a <script> payload is not written as a live tag", "<script>" not in script),
        ("the script payload is HTML-escaped instead", "&lt;script&gt;" in script),
        ("an <img onerror> payload is not written as a live tag", "<img" not in attr.lower()),
    ]


def check_03(m: ModuleType) -> list[Check]:
    with serve(m.build()) as port:
        writer = Client(port)
        writer.post("/comments", form={"author": "u_1042", "body": "Nice work."})
        writer.post(
            "/comments",
            form={"author": "u_1042", "body": "<img src=x onerror=steal()>"},
        )
        writer.post("/comments", form={"author": "u_1042", "body": "<script>evil()</script>"})
        page = Client(port).get("/comments").text

    return [
        ("a plain comment still shows on the page", "Nice work." in page),
        ("a stored <img onerror> is not a live tag", "<img" not in page.lower()),
        ("a stored <script> is not a live tag", "<script>" not in page.lower()),
        ("the stored markup is HTML-escaped instead", "&lt;img" in page.lower()),
    ]


def _login(port: int, email: str, password: str, role: str = "member") -> Client:
    client = Client(port)
    client.post("/login", form={"email": email, "password": password, "role": role})
    return client


def check_04(m: ModuleType) -> list[Check]:
    with serve(m.build()) as port:
        sam = _login(port, "u_1041@acme.test", "hunter2-correct")
        own = sam.get("/invoices/inv_5001")
        other = sam.get("/invoices/inv_5002")
        another = sam.get("/invoices/inv_5003")
        anon = Client(port).get("/invoices/inv_5001")

    def leaked(reply) -> bool:
        return reply.status == 200 and reply.json.get("owner") == "u_1042"

    return [
        (
            f"u_1041 can read their own invoice (got {own.status})",
            own.status == 200 and own.json.get("owner") == "u_1041",
        ),
        (f"u_1041 cannot read u_1042's invoice inv_5002 (got {other.status})", not leaked(other)),
        (
            f"u_1041 cannot read u_1042's invoice inv_5003 (got {another.status})",
            not leaked(another),
        ),
        (f"an unauthenticated request is refused (got {anon.status})", anon.status == 401),
    ]


def check_05(m: ModuleType) -> list[Check]:
    with serve(m.build()) as port:
        admin = _login(port, "u_1099@acme.test", "panther-rooftop-4", role="admin")
        member = _login(port, "u_1041@acme.test", "hunter2-correct", role="member")
        admin_reply = admin.get("/admin/users")
        member_reply = member.get("/admin/users")
        # a member who tries to look like an admin by sending a header the client controls
        forged = member.get("/admin/users", headers={"X-Role": "admin"})
        anon = Client(port).get("/admin/users")

    return [
        (
            f"an admin can read the user list (got {admin_reply.status})",
            admin_reply.status == 200 and len(admin_reply.json.get("users", [])) == 3,
        ),
        (
            f"a member is refused the admin page (got {member_reply.status})",
            member_reply.status == 403,
        ),
        (
            f"a client-sent X-Role header does not grant access (got {forged.status})",
            forged.status == 403,
        ),
        (f"an unauthenticated request is refused (got {anon.status})", anon.status == 401),
    ]


def check_06(m: ModuleType) -> list[Check]:
    with serve(m.build()) as port:
        sam = _login(port, "u_1041@acme.test", "hunter2-correct")
        token = sam.get("/account").json.get("csrf", "")
        with_token = sam.post(
            "/account/email", form={"new_email": "sam.new@acme.test", "csrf": token}
        )
        after_good = sam.get("/account").json.get("email")
        no_token = sam.post("/account/email", form={"new_email": "attacker@evil.test"})
        guessed = sam.post(
            "/account/email", form={"new_email": "attacker@evil.test", "csrf": "csrf"}
        )
        after_bad = sam.get("/account").json.get("email")

    return [
        (
            f"a POST with the issued token changes the email (got {with_token.status})",
            with_token.status == 200 and after_good == "sam.new@acme.test",
        ),
        (f"a POST with no token is refused (got {no_token.status})", no_token.status == 403),
        (f"a POST with a guessed token is refused (got {guessed.status})", guessed.status == 403),
        ("the email is unchanged after the forged posts", after_bad == "sam.new@acme.test"),
    ]


def check_07(m: ModuleType) -> list[Check]:
    with serve(m.build()) as port:
        sam = _login(port, "u_1041@acme.test", "hunter2-correct")
        rename = sam.request("PATCH", "/me", json_body={"display_name": "Sam R."})
        sam.request("PATCH", "/me", json_body={"role": "admin", "token": "tok_self_pick"})
        final = sam.get("/me").json

    return [
        (f"a display-name change is accepted (got {rename.status})", rename.status == 200),
        ("the role stays member after trying to set admin", final.get("role") == "member"),
        ("the api token is not overwritten", final.get("token") == "tok_1041_7af3c1"),
    ]


def check_08(m: ModuleType) -> list[Check]:
    with m.scenario() as client:
        allowed = client.post("/fetch", json_body={"url": "http://images.acme.test/logo.png"})
        metadata = client.post(
            "/fetch", json_body={"url": "http://169.254.169.254/latest/meta-data/iam/token"}
        )
        internal = client.post("/fetch", json_body={"url": "http://metadata.internal/secret"})
        loopback = client.post("/fetch", json_body={"url": "http://localhost/secret"})

    def leaked(reply) -> bool:
        return reply.status == 200 and m.SECRET in reply.json.get("body", "")

    return [
        (f"the allowed image host is still fetched (got {allowed.status})", allowed.status == 200),
        (f"the cloud metadata IP is blocked (got {metadata.status})", not leaked(metadata)),
        (f"the internal host by name is blocked (got {internal.status})", not leaked(internal)),
        (f"the server's own loopback is blocked (got {loopback.status})", not leaked(loopback)),
    ]


def check_09(m: ModuleType) -> list[Check]:
    with m.scenario() as (client, secret_path):
        report = client.get("/files?name=q3-summary.txt")
        up = client.get("/files?name=..%2Fsecret.key")
        absolute = client.get(f"/files?name={_quote(secret_path)}")
        deeper = client.get("/files?name=..%2F..%2Fsecret.key")

    def leaked(reply) -> bool:
        return reply.status == 200 and m.SECRET in reply.text

    return [
        (
            f"a real report is still served (got {report.status})",
            report.status == 200 and "Q3 summary" in report.text,
        ),
        (f"climbing one level up is blocked (got {up.status})", not leaked(up)),
        (f"an absolute path is blocked (got {absolute.status})", not leaked(absolute)),
        (f"a deeper climb is blocked (got {deeper.status})", not leaked(deeper)),
    ]


def check_10(m: ModuleType) -> list[Check]:
    with serve(m.build()) as port:
        client = Client(port)

        def where(value: str) -> str | None:
            return client.get(f"/login?next={_quote(value)}").header("Location")

        local = where("/invoices")
        full = where("https://acme.evil.test/phish")
        relative = where("//acme.evil.test/phish")
        backslash = where("/\\acme.evil.test/phish")
        scheme = where("https:acme.evil.test")

    def off_site(location: str | None) -> bool:
        return bool(location) and "acme.evil.test" in location

    return [
        (f"a local path is still used as the target (got {local!r})", local == "/invoices"),
        (f"a full off-site URL is not used (got {full!r})", not off_site(full)),
        (f"a protocol-relative URL is not used (got {relative!r})", not off_site(relative)),
        (f"a backslash trick is not used (got {backslash!r})", not off_site(backslash)),
        (f"a scheme with no slashes is not used (got {scheme!r})", not off_site(scheme)),
    ]


def _quote(value: str) -> str:
    from urllib.parse import quote

    return quote(value, safe="")


CHECKS: dict[int, Callable[[ModuleType], list[Check]]] = {
    1: check_01,
    2: check_02,
    3: check_03,
    4: check_04,
    5: check_05,
    6: check_06,
    7: check_07,
    8: check_08,
    9: check_09,
    10: check_10,
}
