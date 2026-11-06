"""Case 05: the admin page with no lock on the door.

The admin user list is only linked from the admin menu, so members never see it. But the server
hands it to anyone who asks for the URL. Hiding a link in the page is not access control; the
check has to live on the server, on every request.

Run it: uv run python -m trust run 5
"""

from trust.http import App, Client, Request, Response, serve
from trust.session import Sessions
from trust.store import PEOPLE


def build() -> App:
    sessions = Sessions()

    def app(request: Request) -> Response:
        if request.path == "/login" and request.method == "POST":
            email, role = request.form.get("email", ""), request.form.get("role", "member")
            sid = sessions.sign_in(email, request.form.get("password", ""), role)
            if sid is None:
                return Response(401, {"error": "sign in failed"})
            return Response(200, {"ok": True}).set_cookie(sessions.cookie(sid))

        if request.path == "/admin/users":
            session = sessions.of(request.cookies.get("sid"))
            if session is None:
                return Response(401, {"error": "sign in"})
            # The fix: the server checks the role on this request. Being signed in is not being
            # allowed. A hidden link is not a check.
            if session.role != "admin":
                return Response(403, {"error": "forbidden"})
            users = [
                {"id": uid, "email": email, "role": role, "token": token}
                for uid, email, _, role, _, token in PEOPLE
            ]
            return Response(200, {"users": users})
        return Response(404, {"error": "not found"})

    return app


def sign_in(client: Client, email: str, password: str, role: str = "member") -> None:
    client.post("/login", form={"email": email, "password": password, "role": role})


def run() -> None:
    with serve(build()) as port:
        admin, member = Client(port), Client(port)
        sign_in(admin, "u_1099@acme.test", "panther-rooftop-4", role="admin")
        sign_in(member, "u_1041@acme.test", "hunter2-correct", role="member")
        print("Both are signed in. Both ask for the admin-only user list:\n")
        for label, client in [("u_1099 (admin)", admin), ("u_1041 (member)", member)]:
            reply = client.get("/admin/users")
            users = reply.json.get("users", [])
            tokens = ", ".join(u["token"] for u in users)
            print(f"  {label:<16} GET /admin/users -> {reply.status}, {len(users)} users")
            if users:
                print(f"       tokens on the page: {tokens}")
