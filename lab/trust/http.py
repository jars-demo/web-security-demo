"""A very small web stack for the lab: real HTTP over real sockets on 127.0.0.1.

An app is a function (Request) -> Response. serve(app) runs it on a free port on the loopback
address, and Client talks to it with http.client, keeping cookies the way a browser would for one
site. Bodies can be JSON or form-encoded, and a Response body can be a dict (JSON), a string
(HTML) or bytes. Nothing here reaches past 127.0.0.1.
"""

import http.client
import json
import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlsplit


@dataclass
class Request:
    method: str
    path: str
    query: dict[str, str]
    headers: dict[str, str]
    cookies: dict[str, str]
    raw: bytes

    @property
    def json(self) -> dict:
        if not self.raw:
            return {}
        try:
            value = json.loads(self.raw)
        except ValueError:
            return {}
        return value if isinstance(value, dict) else {}

    @property
    def form(self) -> dict[str, str]:
        if not self.raw:
            return {}
        return {k: v[0] for k, v in parse_qs(self.raw.decode("utf-8", "replace")).items()}


@dataclass
class Response:
    status: int = 200
    body: object = b""
    content_type: str | None = None
    headers: list[tuple[str, str]] = field(default_factory=list)

    def with_header(self, name: str, value: str) -> "Response":
        self.headers.append((name, value))
        return self

    def set_cookie(self, value: str) -> "Response":
        self.headers.append(("Set-Cookie", value))
        return self

    def rendered(self) -> tuple[bytes, str]:
        """Return the body as bytes and the content type to send it with."""
        if isinstance(self.body, bytes):
            return self.body, self.content_type or "application/octet-stream"
        if isinstance(self.body, str):
            return self.body.encode("utf-8"), self.content_type or "text/html; charset=utf-8"
        data = json.dumps(self.body).encode("utf-8")
        return data, self.content_type or "application/json"


App = Callable[[Request], Response]


def handler_for(app: App) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def handle_one(self) -> None:
            url = urlsplit(self.path)
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b""
            cookies = SimpleCookie(self.headers.get("Cookie", ""))
            request = Request(
                method=self.command,
                path=url.path,
                query={k: v[0] for k, v in parse_qs(url.query).items()},
                headers={k.lower(): v for k, v in self.headers.items()},
                cookies={name: morsel.value for name, morsel in cookies.items()},
                raw=raw,
            )
            try:
                response = app(request)
            except Exception:  # a crash is a 500, not a dropped connection
                response = Response(500, {"error": "internal error"})
            data, content_type = response.rendered()
            self.send_response(response.status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            for name, value in response.headers:
                self.send_header(name, value)
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(data)

        do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = handle_one

        def log_message(self, format: str, *args: object) -> None:
            pass

    return Handler


@contextmanager
def serve(app: App) -> Iterator[int]:
    """Run the app on a free port on 127.0.0.1 and yield the port. Closes the server after."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_for(app))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield server.server_address[1]
    finally:
        server.shutdown()
        server.server_close()


@dataclass
class Reply:
    status: int
    raw: bytes
    headers: list[tuple[str, str]]

    @property
    def text(self) -> str:
        return self.raw.decode("utf-8", "replace")

    @property
    def json(self) -> dict:
        try:
            value = json.loads(self.raw or b"{}")
        except ValueError:
            return {}
        return value if isinstance(value, dict) else {}

    def header(self, name: str) -> str | None:
        return next((v for k, v in self.headers if k.lower() == name.lower()), None)

    def set_cookies(self) -> list[str]:
        return [v for k, v in self.headers if k.lower() == "set-cookie"]


class Client:
    """One browser profile: it keeps the cookies the site sets and sends them back to it. It does
    not follow redirects, so a test can see the Location header itself."""

    def __init__(self, port: int) -> None:
        self.port = port
        self.cookies: dict[str, str] = {}

    def request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict | None = None,
        form: dict | None = None,
        headers: dict[str, str] | None = None,
    ) -> Reply:
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        send_headers = dict(headers or {})
        payload: bytes | None = None
        if json_body is not None:
            payload = json.dumps(json_body).encode("utf-8")
            send_headers.setdefault("Content-Type", "application/json")
        elif form is not None:
            payload = urlencode(form).encode("utf-8")
            send_headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
        if self.cookies:
            send_headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in self.cookies.items())
        connection.request(method, path, body=payload, headers=send_headers)
        response = connection.getresponse()
        reply = Reply(response.status, response.read(), response.getheaders())
        connection.close()
        for value in reply.set_cookies():
            for name, morsel in SimpleCookie(value).items():
                if morsel["max-age"] == "0" or morsel.value == "":
                    self.cookies.pop(name, None)
                else:
                    self.cookies[name] = morsel.value
        return reply

    def get(self, path: str, headers: dict[str, str] | None = None) -> Reply:
        return self.request("GET", path, headers=headers)

    def post(
        self,
        path: str,
        *,
        json_body: dict | None = None,
        form: dict | None = None,
        headers: dict[str, str] | None = None,
    ) -> Reply:
        return self.request("POST", path, json_body=json_body, form=form, headers=headers)
