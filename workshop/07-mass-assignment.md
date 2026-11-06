# The profile update that granted admin

> The profile editor saves every field the request sends, including the ones the form never showed: role and token.

**Time:** 22 minutes

## Goal

After this chapter you can recognise mass assignment, explain why binding a whole request body to a
record is dangerous, and fix it with an allowlist of the fields a request may change.

## The idea

It is convenient to take a request body, a dictionary of fields, and write every field into the
matching record. One line updates the whole row, and when you add a column the code already handles
it. That convenience is the bug. The request body is attacker-controlled, and the record has
columns the form was never meant to touch: the user's role, their API token, a `verified` flag, a
`balance`. If the handler writes whatever keys arrive, the attacker simply sends the keys that are
not on the form.

This is mass assignment, also called autobinding or over-posting. The profile form shows a display
name, so a member expects to change their display name. The handler binds the whole body, so the
member sends `role: admin` alongside, and becomes an admin. Nothing in the form offered that field.
The attacker did not need it to.

The fix is an allowlist. Decide which fields this operation may change, and ignore every other key
in the body. An allowlist is safe as the system grows: a new sensitive column is excluded by
default, because it is not on the list. A blocklist is the opposite trap. You block `role` after an
incident, and the next sensitive column, `token`, is still open, because you can only block the
holes you already know about.

Where is the convenient approach acceptable? Almost nowhere for data that crosses a trust boundary.
Internal, fully-trusted callers are a different story, but anything that takes a request from a
browser or a public API should name the fields it accepts. Frameworks call this strong parameters,
serializer fields, or a schema; they all mean the same thing, bind only what you named.

## The case

```text
case 07: The profile update that granted admin

Before: {'id': 'u_1041', 'role': 'member', 'token': 'tok_1041_7af3c1'}

u_1041 PATCHes a new display name, and slips in role and token:
  PATCH /me -> 200
  After:  {'id': 'u_1041', 'role': 'admin', 'token': 'tok_self_pick'}
```

```bash
uv run python -m trust run 7
```

The member starts as a member. One PATCH that also carries `role` and `token` makes them an admin
and lets them choose their own API token. The display name was the cover story.

## Reasoning towards the fix

Open `lab/cases/case07_mass_assignment.py`. The PATCH handler loops over every key in the body and
runs an `UPDATE` for each one. That loop is the problem: it trusts the set of keys.

Define the set of columns a profile edit may change, for example display name and email, and update
only those. Skip any key that is not in the set. Do not reach for a blocklist that drops `role`
alone; the token is just as sensitive, and the next column will be too. Name what is allowed and
ignore the rest.

## Check your fix

As shipped:

```text
  PASS  a display-name change is accepted (got 200)
  FAIL  the role stays member after trying to set admin
  FAIL  the api token is not overwritten
```

```bash
uv run python -m trust check 7
```

The passing line keeps the real edit working. The two failing lines try to set the role and the
token, and expect both to be ignored. A fix that blocks only `role` passes the role line and still
fails on the token, which is exactly why a blocklist is the wrong shape.

## In production

- Bind request bodies to an explicit schema or a named set of fields. Let unknown and unlisted
  fields be ignored or rejected, never applied.
- Keep sensitive fields (role, permissions, ownership, balances, verification flags) out of any
  mass update path. Change them through their own audited operations.
- Watch for the convenience helpers: `update(**body)`, `Model(**request.json)`, `setattr` loops.
  They are where mass assignment hides.
- Test that a request carrying a privileged field leaves that field unchanged. Make it part of the
  suite, because the vulnerable version passes the happy-path test.

## Key points

- Binding a whole request body to a record lets the client write fields the form never showed.
- An allowlist of editable fields is safe as the schema grows; a blocklist leaks the next field.
- Keep privileged fields off the general update path and behind their own operations.
- Frameworks' strong parameters and schemas exist for exactly this; use them.
- Test the over-posting case, because the happy path looks fine.
