"""Case 04: the invoice with someone else's name on it.

You have to be signed in to read an invoice. The handler checks that, and then reads whatever id
the URL names. It never checks that the invoice belongs to the person asking. Change the number
in the URL and you read someone else's invoice.

Run it: uv run python -m trust run 4
"""

from trust.http import App, Client, Request, Response, serve
from trust.session import Sessions

INVOICES = {
    "inv_5001": ("u_1041", 4200, "Design retainer, March"),
    "inv_5002": ("u_1042", 98000, "Legal settlement, confidential"),
    "inv_5003": ("u_1042", 1500, "Taxi receipts"),
}


def build() -> App:
    sessions = Sessions()

    def app(request: Request) -> Response:
        if request.path == "/login" and request.method == "POST":
            email, role = request.form.get("email", ""), request.form.get("role", "member")
            sid = sessions.sign_in(email, request.form.get("password", ""), role)
            if sid is None:
                return Response(401, {"error": "sign in failed"})
            return Response(200, {"ok": True}).set_cookie(sessions.cookie(sid))

        if request.path.startswith("/invoices/"):
            session = sessions.of(request.cookies.get("sid"))
            if session is None:
                return Response(401, {"error": "sign in"})
            invoice_id = request.path.removeprefix("/invoices/")
            row = INVOICES.get(invoice_id)
            if row is None:
                return Response(404, {"error": "no such invoice"})
            # The fix: the invoice is only returned if it belongs to the person asking. A mismatch
            # is a 404, so the handler does not even confirm the id exists.
            owner, amount_cents, memo = row
            if owner != session.user:
                return Response(404, {"error": "no such invoice"})
            return Response(
                200, {"id": invoice_id, "owner": owner, "cents": amount_cents, "memo": memo}
            )
        return Response(404, {"error": "not found"})

    return app


def sign_in(client: Client, email: str, password: str, role: str = "member") -> None:
    client.post("/login", form={"email": email, "password": password, "role": role})


def run() -> None:
    with serve(build()) as port:
        sam = Client(port)
        sign_in(sam, "u_1041@acme.test", "hunter2-correct")
        print("u_1041 signs in, then asks for invoices by number:\n")
        for invoice_id in ["inv_5001", "inv_5002", "inv_5003"]:
            body = sam.get(f"/invoices/{invoice_id}").json
            print(
                f"  GET /invoices/{invoice_id} -> owner {body.get('owner')}, {body.get('memo')!r}"
            )
