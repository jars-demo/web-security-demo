# The form that any site could submit

> Changing the account email trusts the session cookie and nothing else. The browser attaches that cookie to requests from any site.

**Time:** 24 minutes

## Goal

After this chapter you can explain why a cookie alone cannot prove a request was intended, describe
cross-site request forgery, and defend a state-changing request with a token the session knows and
another site cannot read.

## The idea

Cookies have one property that is both their strength and their weakness: the browser sends them
automatically, on every request to the site they belong to, no matter which page started the
request. A form on another site, or an image tag, or a background fetch, can aim a request at your
app, and the browser attaches the victim's session cookie because the request is going to your
domain. The server sees a valid session and does what it is told.

That is cross-site request forgery. The attacker does not steal the cookie or see any response.
They do not need to. They only need the victim, while signed in to your app, to load a page the
attacker controls. That page sends a request to change the victim's email, and the cookie rides
along. The request looks exactly like a real one, because in every respect the server can see, it
is one.

The defence is to require something on each state-changing request that a real page can include and
a foreign page cannot obtain. The classic answer is a synchronizer token: the server issues a
random token tied to the session, puts it in the real form, and requires it back on submit. A
cross-site page cannot read your page to learn the token (the same-origin policy forbids it), so it
cannot forge the request. The token must be per-session and unguessable, and the server must compare
it to the session's own token, not merely check that some token is present.

Two things people get wrong. First, `SameSite` cookies help a lot and are worth setting, but they
are a defence in depth, not a complete answer: their behaviour varies across request types and
older clients, so a token is still the control. Second, only state-changing requests need the token.
Safe methods (GET, HEAD) must not change state in the first place; if a GET mutates data, no token
scheme will save you.

## The case

```text
case 06: The form that any site could submit

u_1041 is signed in. Account email: u_1041@acme.test

A forged POST (the kind another site can trigger) rides the cookie, sends no token:
  POST /account/email -> 200
  Account email is now: attacker@evil.test
```

```bash
uv run python -m trust run 6
```

The request carries the session cookie and no token at all, and the email changes. An attacker who
can get a signed-in user to load one page can point the account's email, and the password reset that
follows, at an address they control.

## Reasoning towards the fix

Open `lab/cases/case06_csrf.py`. There is already a `GET /account` that returns the session's CSRF
token, and the session object carries that token. The POST handler ignores it. So the pieces are in
place; the handler just has to require them.

In the POST handler, read the submitted `csrf` value and compare it to the session's token. If it is
missing or does not match, return 403 before changing anything. A real page fetches the token from
`GET /account` and sends it; a cross-site page cannot read that token, so it cannot pass the check.
Do not accept any non-empty token, and do not hardcode one; the token has to be the session's.

## Check your fix

As shipped:

```text
  PASS  a POST with the issued token changes the email (got 200)
  FAIL  a POST with no token is refused (got 200)
  FAIL  a POST with a guessed token is refused (got 200)
  FAIL  the email is unchanged after the forged posts
```

```bash
uv run python -m trust check 6
```

The passing line keeps the real feature working: a POST that carries the issued token succeeds. The
failing lines send no token and a guessed token, and expect both to be refused and the email left
alone. A fix that accepts any token passes the first and fails the guessed-token line.

## In production

- Use your framework's CSRF protection. It issues and checks the token for you and handles the
  per-session binding and constant-time comparison.
- Set session cookies `SameSite=Lax` or `Strict` and `Secure` and `HttpOnly`. This is a strong
  second layer under the token, not a replacement.
- Keep safe methods safe: GET must never change state. Audit any GET that writes.
- For token APIs used by non-browser clients, a bearer token in a header is not sent automatically
  by the browser, so those endpoints are not CSRF-prone the same way; know which auth model each
  endpoint uses.

## Key points

- The browser sends cookies on cross-site requests, so a cookie cannot prove intent.
- CSRF makes the victim's browser send a real-looking request the victim never meant to send.
- Require a per-session, unguessable token on every state-changing request and compare it to the
  session's own.
- `SameSite` cookies are defence in depth, not the whole defence.
- Safe methods must not mutate state; a token cannot protect a GET that writes.
