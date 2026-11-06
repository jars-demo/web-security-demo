"""Case 06: the form that any site could submit.

Changing the account email is a POST that trusts the session cookie and nothing else. The browser
attaches that cookie to any request to this site, including one triggered by a different site the
user is also visiting. With no unguessable token tied to the session, a form on any page can post
here as the signed-in user.

Run it: uv run python -m trust run 6
"""

from trust.http import App, Client, Request, Response, serve
from trust.session import Sessions
from trust.store import PEOPLE


def build() -> App:
    sessions = Sessions()
    email_of = {uid: email for uid, email, *_ in PEOPLE}

    def app(request: Request) -> Response:
        if request.path == "/login" and request.method == "POST":
            sid = sessions.sign_in(
                request.form.get("email", ""), request.form.get("password", ""), "member"
            )
            if sid is None:
                return Response(401, {"error": "sign in failed"})
            return Response(200, {"ok": True}).set_cookie(sessions.cookie(sid))

        session = sessions.of(request.cookies.get("sid"))
        if session is None:
            return Response(401, {"error": "sign in"})

        if request.path == "/account" and request.method == "GET":
            return Response(200, {"email": email_of[session.user], "csrf": session.csrf})

        if request.path == "/account/email" and request.method == "POST":
            # The bug: the only thing proving this request is wanted is the session cookie, which
            # the browser sends on every request to this site, wherever it came from.
            email_of[session.user] = request.form.get("new_email", "")
            return Response(200, {"email": email_of[session.user]})
        return Response(404, {"error": "not found"})

    return app


def run() -> None:
    with serve(build()) as port:
        sam = Client(port)
        sam.post("/login", form={"email": "u_1041@acme.test", "password": "hunter2-correct"})
        before = sam.get("/account").json["email"]
        print(f"u_1041 is signed in. Account email: {before}\n")
        print("A forged POST (the kind another site can trigger) rides the cookie, sends no token:")
        forged = sam.post("/account/email", form={"new_email": "attacker@evil.test"})
        print(f"  POST /account/email -> {forged.status}")
        print(f"  Account email is now: {sam.get('/account').json['email']}")
