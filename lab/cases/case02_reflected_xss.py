"""Case 02: the search box that ran its input.

The search page writes back whatever you typed, straight into the HTML. A query that contains
markup is sent to the next visitor's browser as markup. A crafted link turns the search box into
a way to run code in someone else's session.

Run it: uv run python -m trust run 2
"""

from trust.http import App, Client, Request, Response, serve

DOCS = ["Q3 revenue memo", "Payroll export", "Security review notes", "Board deck draft"]


def build() -> App:
    def app(request: Request) -> Response:
        if request.path == "/search":
            term = request.query.get("q", "")
            hits = [d for d in DOCS if term.lower() in d.lower()] if term else []
            items = "".join(f"<li>{d}</li>" for d in hits)

            # The bug: the search term is dropped into the page as-is. If it contains HTML, the
            # browser builds that HTML.
            page = (
                "<!doctype html><html><body>"
                "<h1>Search</h1>"
                f"<p>You searched for: {term}</p>"
                f"<ul>{items}</ul>"
                "</body></html>"
            )
            return Response(200, page)
        return Response(404, {"error": "not found"})

    return app


def run() -> None:
    with serve(build()) as port:
        client = Client(port)
        print("A normal search, then a search for a script tag:\n")
        for label, term in [
            ("plain term 'revenue'", "revenue"),
            ("a <script> payload", "<script>fetch('/steal?c='+document.cookie)</script>"),
            ("an <img onerror> payload", '"><img src=x onerror=alert(document.domain)>'),
        ]:
            body = client.get(f"/search?q={_q(term)}").text
            line = next(li for li in body.split("<p>") if "searched" in li).split("</p>")[0]
            print(f"  {label}:")
            print(f"       {line}")


def _q(term: str) -> str:
    from urllib.parse import quote

    return quote(term, safe="")
