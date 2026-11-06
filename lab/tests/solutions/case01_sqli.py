"""Case 01: the quote that rewrote the query.

The login handler builds its SQL by pasting the email and password straight into the query
string. A value with a quote in it stops being data and becomes part of the query. One crafted
email signs in with no password at all, as whoever you name.

Run it: uv run python -m trust run 1
"""

from trust.http import App, Request, Response, serve
from trust.store import connect, seed_people


def build() -> App:
    db = connect()
    seed_people(db)

    def app(request: Request) -> Response:
        if request.path == "/login" and request.method == "POST":
            email = request.form.get("email", "")
            password = request.form.get("password", "")

            # The fix: the values are bound as parameters. The database treats them as data, so a
            # quote is just a quote, never part of the query.
            query = "SELECT id, role FROM users WHERE email = ? AND password = ?"
            row = db.execute(query, (email, password)).fetchone()

            if row is None:
                return Response(401, {"error": "wrong email or password", "sql": query})
            return Response(200, {"user": row["id"], "role": row["role"], "sql": query})
        return Response(404, {"error": "not found"})

    return app


def run() -> None:
    with serve(build()) as port:
        from trust.http import Client

        def login(label: str, email: str, password: str) -> None:
            reply = Client(port).post("/login", form={"email": email, "password": password})
            body = reply.json
            who = body.get("user") or body.get("error")
            print(f"  {label:<34} -> {reply.status}  {who}")
            print(f"       sql: {body.get('sql')}")

        print("A real sign-in, a wrong password, then two crafted emails:\n")
        login("u_1041 with the right password", "u_1041@acme.test", "hunter2-correct")
        login("u_1041 with a wrong password", "u_1041@acme.test", "nope")
        login("the OR-always-true email", "x' OR '1'='1' -- ", "anything")
        login("sign in as the admin, no password", "u_1099@acme.test' -- ", "anything")
