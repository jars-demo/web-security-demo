"""Case 08: the fetch that reached the metadata service.

The avatar importer takes a URL and the server fetches it. The server sits on a network the user
cannot reach, next to internal services with no login of their own. A URL that names one of those
services makes the server fetch it and hand back the answer.

Everything here runs on 127.0.0.1. The "internal" service is a lab stand-in for a cloud metadata
endpoint; no real host is ever contacted.

Run it: uv run python -m trust run 8
"""

from collections.abc import Iterator
from contextlib import contextmanager
from http.client import HTTPConnection
from urllib.parse import urlsplit

from trust.http import App, Client, Request, Response, serve

SECRET = "root-token=ssrf_9c12e7f0"
ALLOWED = {"images.acme.test"}


def fetch(url: str, resolver: dict[str, tuple[str, int]]) -> tuple[int, str]:
    """Fetch a URL on behalf of the user and return (status, first line of the body)."""
    parts = urlsplit(url)
    host = parts.hostname or ""

    # The bug: any host the server can reach is fetched. The server can reach the internal
    # network, so the user can too, through this handler.
    if host not in resolver:
        return 0, "could not resolve host"
    ip, port = resolver[host]
    conn = HTTPConnection(ip, port, timeout=5)
    conn.request("GET", parts.path or "/")
    response = conn.getresponse()
    body = response.read().decode("utf-8", "replace").splitlines()
    conn.close()
    return response.status, (body[0] if body else "")


def _image_app() -> App:
    def app(_: Request) -> Response:
        body = b"\x89PNG\r\n\x1a\n" + b"lab-logo-bytes " * 8
        return Response(200, body, content_type="image/png")

    return app


def _internal_app() -> App:
    def app(_: Request) -> Response:
        return Response(200, SECRET, content_type="text/plain")

    return app


def build(resolver: dict[str, tuple[str, int]]) -> App:
    def app(request: Request) -> Response:
        if request.path == "/fetch" and request.method == "POST":
            status, head = fetch(request.json.get("url", ""), resolver)
            if status == 0:
                return Response(400, {"error": head})
            return Response(200, {"fetched_status": status, "body": head})
        return Response(404, {"error": "not found"})

    return app


@contextmanager
def scenario() -> Iterator[Client]:
    """Start the allowed image host and the internal service, both on 127.0.0.1, and yield a
    client pointed at the avatar importer."""
    with serve(_image_app()) as image_port, serve(_internal_app()) as internal_port:
        resolver = {
            "images.acme.test": ("127.0.0.1", image_port),
            "metadata.internal": ("127.0.0.1", internal_port),
            "169.254.169.254": ("127.0.0.1", internal_port),
            "localhost": ("127.0.0.1", internal_port),
        }
        with serve(build(resolver)) as port:
            yield Client(port)


def run() -> None:
    with scenario() as client:
        print("The importer should only fetch the avatar host. Four URLs go in:\n")
        for label, url in [
            ("the allowed image host", "http://images.acme.test/logo.png"),
            ("the cloud metadata IP", "http://169.254.169.254/latest/meta-data/iam/token"),
            ("an internal service by name", "http://metadata.internal/secret"),
            ("the server's own loopback", "http://localhost/secret"),
        ]:
            reply = client.post("/fetch", json_body={"url": url})
            body = reply.json
            got = body.get("body") if reply.status == 200 else body.get("error")
            print(f"  {label:<28} -> {reply.status}  {got!r}")
