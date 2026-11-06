# The admin page with no lock on the door

> The admin user list is only linked from the admin menu. The server hands it to anyone who asks for the URL.

**Time:** 22 minutes

## Goal

After this chapter you can tell function-level access control from object-level, explain why hiding
a link is not a control, and enforce a role check on the server for every protected route.

## The idea

The last chapter was about the wrong object. This one is about the wrong function: an endpoint that
a whole class of users should not be able to call at all. The admin user list is meant for admins.
The UI knows that, so it only shows the link to admins. But the link is a hint for humans, not a
rule for the server. Anyone can type the URL, read it from the page source, or find it in a
JavaScript bundle. This is forced browsing, and it works whenever the only thing standing between a
member and an admin page is that the member was not shown the door.

Access control has to run on the server, on every request, from a fact the server trusts. The fact
here is the role stored in the session. Not a role in a cookie the client can edit, not a header the
client sets, not a hidden form field. Those are all client-controlled, and the whole point is that
the client is the one you are guarding against.

The deeper lesson is that access control must be deny-by-default. A new endpoint should be
unreachable until someone grants access, not reachable until someone remembers to lock it. The
industry keeps relearning this because the failure is invisible in testing: the admin, who writes
and tests the feature, always has access, so it always looks fine. The member who can also reach it
is never in the test.

When is "the UI hides it" acceptable? As a usability choice on top of a server check, never instead
of one. Hiding the link is fine. Relying on the hidden link is the bug.

## The case

```text
case 05: The admin page with no lock on the door

Both are signed in. Both ask for the admin-only user list:

  u_1099 (admin)   GET /admin/users -> 200, 3 users
       tokens on the page: tok_1041_7af3c1, tok_1042_2bd9e0, tok_1099_ff21aa
  u_1041 (member)  GET /admin/users -> 200, 3 users
       tokens on the page: tok_1041_7af3c1, tok_1042_2bd9e0, tok_1099_ff21aa
```

```bash
uv run python -m trust run 5
```

The admin and the member get the same answer: the full user list, including every user's API
token. The member was never shown the link. It made no difference.

## Reasoning towards the fix

Open `lab/cases/case05_access_control.py`. The handler loads the session and checks that it exists,
then builds the list. "Signed in" is the only gate. The session already carries the role, so the
missing step is to check it.

After the signed-in check, return 403 unless the session role is admin. Take the role from the
session, which the server set at sign-in, not from any header or field the request carries. A fix
that trusts a client-supplied role just moves the hole.

## Check your fix

As shipped:

```text
  PASS  an admin can read the user list (got 200)
  FAIL  a member is refused the admin page (got 200)
  FAIL  a client-sent X-Role header does not grant access (got 200)
  PASS  an unauthenticated request is refused (got 401)
```

```bash
uv run python -m trust check 5
```

One failing line sends an `X-Role: admin` header from a member. The fix must ignore it, because the
role has to come from the server's own session, not from the request. The admin keeps access and
the signed-out caller is still refused.

## In production

- Enforce authorization in one place that every protected route passes through: a decorator,
  middleware, or a policy layer. Scattered `if role == 'admin'` checks are easy to forget on the
  next endpoint.
- Default to deny. New routes should require an explicit grant. Prefer a framework where a missing
  policy means no access.
- Never trust a role, tenant, or permission that arrives from the client. Derive it on the server
  from the authenticated session.
- Test the negative case. For every admin route, add a test where a member calls it and expects a
  403. The member is the test your manual testing never runs.

## Key points

- Hiding a link is a UI nicety, not access control.
- Enforce the role check on the server, on every request, from the trusted session.
- Function-level access control must be deny-by-default, or new endpoints ship open.
- Client-supplied roles and headers are input from the adversary; ignore them for authorization.
- The vulnerable code looks complete, so write the member-is-refused test.
