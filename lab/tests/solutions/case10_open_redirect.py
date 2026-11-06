"""Case 10: the login link that pointed off-site.

After sign-in the app sends you where you were going, taken from the next parameter. The handler
puts that value straight into the redirect. A link to the real site, with next set to another
site, lands the user on the other site, still trusting the address bar they started from.

Run it: uv run python -m trust run 10
"""

from trust.http import App, Client, Request, Response, serve


def build() -> App:
    def app(request: Request) -> Response:
        if request.path == "/login":
            target = request.query.get("next", "/")
            # The fix: only a path on this site is allowed. // and /\ and a bare scheme all send
            # the browser elsewhere, so anything but a single leading / falls back to /.
            if not target.startswith("/") or target.startswith("//") or target.startswith("/\\"):
                target = "/"
            return Response(302, {"going_to": target}).with_header("Location", target)
        return Response(404, {"error": "not found"})

    return app


def run() -> None:
    with serve(build()) as port:
        client = Client(port)
        print("Sign-in redirects to next. Five values, same trusted login link:\n")
        for label, value in [
            ("a page on the site", "/invoices"),
            ("a full off-site URL", "https://acme.evil.test/phish"),
            ("protocol-relative", "//acme.evil.test/phish"),
            ("backslash trick", "/\\acme.evil.test/phish"),
            ("scheme with no slashes", "https:acme.evil.test"),
        ]:
            reply = client.get(f"/login?next={_q(value)}")
            print(f"  {label:<24} next={value!r}")
            print(f"       -> {reply.status}  Location: {reply.header('Location')!r}")


def _q(value: str) -> str:
    from urllib.parse import quote

    return quote(value, safe="")
