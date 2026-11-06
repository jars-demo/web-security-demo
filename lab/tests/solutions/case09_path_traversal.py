"""Case 09: the download that climbed out of its folder.

Report files live in one folder, and the download handler serves a file by name from it. The name
comes from the request, and the handler joins it onto the folder without checking where it lands.
A name with ../ in it, or an absolute path, reads a file the folder was meant to keep in.

Everything here happens inside one temporary folder the lab makes and deletes. No real system file
is read.

Run it: uv run python -m trust run 9
"""

import os
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager

from trust.http import App, Client, Request, Response, serve

SECRET = "signing-key=pt_4d7b2a90"


def build(base: str) -> App:
    def app(request: Request) -> Response:
        if request.path == "/files":
            name = request.query.get("name", "")
            # The fix: resolve the final path and confirm it is still inside the reports folder
            # before opening it. Checking the name for ".." is not enough.
            full = os.path.realpath(os.path.join(base, name))
            if not full.startswith(os.path.realpath(base) + os.sep):
                return Response(404, {"error": "no such file"})
            try:
                with open(full, encoding="utf-8") as handle:
                    return Response(200, handle.read(), content_type="text/plain")
            except (FileNotFoundError, IsADirectoryError, PermissionError):
                return Response(404, {"error": "no such file"})
        return Response(404, {"error": "not found"})

    return app


@contextmanager
def scenario() -> Iterator[tuple[Client, str]]:
    """Make a temp tree: a reports folder with two files, and a secret one level above it, next to
    the reports folder. Yields a client and the absolute path of the secret."""
    root = tempfile.mkdtemp(prefix="web-security-lab-pt-")
    base = os.path.join(root, "reports")
    os.makedirs(base)
    with open(os.path.join(base, "q3-summary.txt"), "w", encoding="utf-8") as handle:
        handle.write("Q3 summary: revenue up 4 percent.\n")
    with open(os.path.join(base, "handbook.txt"), "w", encoding="utf-8") as handle:
        handle.write("Company handbook, public section.\n")
    secret_path = os.path.join(root, "secret.key")
    with open(secret_path, "w", encoding="utf-8") as handle:
        handle.write(SECRET + "\n")
    try:
        with serve(build(base)) as port:
            yield Client(port), secret_path
    finally:
        for folder, _, files in os.walk(root, topdown=False):
            for name in files:
                os.remove(os.path.join(folder, name))
            os.rmdir(folder)


def run() -> None:
    with scenario() as (client, secret_path):
        print("The reports folder holds two files. A secret sits one level above it.\n")
        for label, name in [
            ("a real report", "q3-summary.txt"),
            ("climb one level up", "../secret.key"),
            ("an absolute path", secret_path),
        ]:
            reply = client.get(f"/files?name={_q(name)}")
            shown = reply.text.strip() if reply.status == 200 else reply.json.get("error")
            print(f"  {label:<22} name={name!r}")
            print(f"       -> {reply.status}  {shown!r}")


def _q(value: str) -> str:
    from urllib.parse import quote

    return quote(value, safe="")
