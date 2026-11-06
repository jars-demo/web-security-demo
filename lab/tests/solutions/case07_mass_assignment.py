"""Case 07: the profile update that granted admin.

The profile editor lets you change your display name. The handler saves every field the request
sends, so the request can also send fields the form never showed: role, and the API token. One
PATCH turns a member into an admin.

Run it: uv run python -m trust run 7
"""

from trust.http import App, Client, Request, Response, serve
from trust.session import Sessions
from trust.store import connect, seed_people


def build() -> App:
    sessions = Sessions()
    db = connect()
    seed_people(db)

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

        if request.path == "/me" and request.method == "GET":
            row = db.execute("SELECT * FROM users WHERE id = ?", (session.user,)).fetchone()
            return Response(200, {"id": row["id"], "role": row["role"], "token": row["token"]})

        if request.path == "/me" and request.method == "PATCH":
            # The fix: an allowlist decides which columns a profile edit may change. Every other
            # key in the body is ignored, so role and token cannot be set here.
            body = request.json
            editable = {"display_name", "email"}
            for column, value in body.items():
                if column not in editable:
                    continue
                db.execute(f"UPDATE users SET {column} = ? WHERE id = ?", (value, session.user))
            db.commit()
            row = db.execute("SELECT * FROM users WHERE id = ?", (session.user,)).fetchone()
            return Response(200, {"id": row["id"], "role": row["role"], "token": row["token"]})
        return Response(404, {"error": "not found"})

    return app


def run() -> None:
    with serve(build()) as port:
        sam = Client(port)
        sam.post("/login", form={"email": "u_1041@acme.test", "password": "hunter2-correct"})
        print(f"Before: {sam.get('/me').json}\n")
        print("u_1041 PATCHes a new display name, and slips in role and token:")
        after = sam.request(
            "PATCH",
            "/me",
            json_body={"display_name": "Sam R.", "role": "admin", "token": "tok_self_pick"},
        )
        print(f"  PATCH /me -> {after.status}")
        print(f"  After:  {after.json}")
