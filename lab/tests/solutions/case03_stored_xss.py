"""Case 03: the comment that ran on every visit.

Comments are saved as typed and written back into the page as typed. A reflected payload needs a
crafted link; a stored one does not. It sits in the database and runs in the browser of everyone
who opens the page, for as long as the row is there.

Run it: uv run python -m trust run 3
"""

from html import escape

from trust.http import App, Client, Request, Response, serve


def build() -> App:
    comments: list[tuple[str, str]] = []  # (author, body)

    def app(request: Request) -> Response:
        if request.path == "/comments" and request.method == "POST":
            comments.append((request.form.get("author", "?"), request.form.get("body", "")))
            return Response(200, {"stored": True})
        if request.path == "/comments":
            # The fix: each author and body is escaped for HTML at render time, so stored markup
            # is shown as text to every reader.
            rows = "".join(
                f"<li><b>{escape(author)}</b>: {escape(body)}</li>" for author, body in comments
            )
            page = f"<!doctype html><html><body><h1>Comments</h1><ul>{rows}</ul></body></html>"
            return Response(200, page)
        return Response(404, {"error": "not found"})

    return app


def run() -> None:
    with serve(build()) as port:
        writer = Client(port)
        writer.post("/comments", form={"author": "u_1042", "body": "Great write-up, thanks."})
        writer.post(
            "/comments",
            form={"author": "u_1042", "body": "<img src=x onerror=fetch('/x?c='+document.cookie)>"},
        )
        print("u_1042 left two comments. Now u_1041 opens the page:\n")
        body = Client(port).get("/comments").text
        for line in body.split("<li>")[1:]:
            print(f"  <li>{line.split('</li>')[0]}")
