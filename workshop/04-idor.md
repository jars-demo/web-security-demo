# The invoice with someone else's name on it

> You must be signed in to read an invoice. Nothing checks the invoice is yours. Change the number in the URL.

**Time:** 22 minutes

## Goal

After this chapter you can recognise an insecure direct object reference, explain why
authentication is not authorization, and add an ownership check that fails closed.

## The idea

Authentication answers "who are you". Authorization answers "are you allowed to touch this". They
are different questions, and a handler that asks only the first has a hole. The invoice endpoint
checks that you are signed in, then reads whatever invoice id the URL names. It never asks whether
that invoice belongs to you.

This is an insecure direct object reference: the request names an object directly, by its id, and
the server trusts the id without checking the caller against the object. The ids do not have to be
guessable. Sequential integers make it trivial to walk every record, but even random ids leak,
through referrer headers, shared links, browser history, and logs. "Hard to guess" is not a control.
The control is the check.

Where should the check live? As close to the data as you can put it. The strongest version is to
fold ownership into the query itself: `WHERE id = ? AND owner = ?`. Then a row either belongs to the
caller or does not come back at all. The next best is to load the row and compare its owner to the
session before returning it. Either way the decision is made on the server from the session, never
from anything the client sent.

One subtle choice: return 404, not 403, when the object is not yours. A 403 confirms the id exists,
which itself leaks information. A 404 says only "nothing here for you". The usual advice to "return
the right status code" is wrong when the right-looking code tells the attacker they found something.

## The case

```text
case 04: The invoice with someone else's name on it

u_1041 signs in, then asks for invoices by number:

  GET /invoices/inv_5001 -> owner u_1041, 'Design retainer, March'
  GET /invoices/inv_5002 -> owner u_1042, 'Legal settlement, confidential'
  GET /invoices/inv_5003 -> owner u_1042, 'Taxi receipts'
```

```bash
uv run python -m trust run 4
```

u_1041 owns only the first invoice. The next two belong to u_1042, including one marked
confidential, and u_1041 reads them all just by changing the number.

## Reasoning towards the fix

Open `lab/cases/case04_idor.py`. The handler loads the session (good) and then looks up the invoice
by id and returns it. The session user is right there, and the invoice row carries its owner. The
one missing line compares them.

Add the check before you return the invoice: if the owner is not the session user, return a 404.
Do not special-case the one id that leaked in the demo; the fix has to hold for every row. The
cleanest version pushes the owner into the lookup so a foreign row never loads at all.

## Check your fix

As shipped:

```text
  PASS  u_1041 can read their own invoice (got 200)
  FAIL  u_1041 cannot read u_1042's invoice inv_5002 (got 200)
  FAIL  u_1041 cannot read u_1042's invoice inv_5003 (got 200)
  PASS  an unauthenticated request is refused (got 401)
```

```bash
uv run python -m trust check 4
```

The check reads two different invoices that belong to someone else, so a fix that just blocks one
id still fails. The owner can still read their own, and a signed-out request is still refused.

## In production

- Scope every read and write by the current user, ideally in the query. Make "filter by owner" the
  default path in your data layer so a new endpoint is safe unless someone opts out.
- Return 404 for objects the caller may not see, so the response does not confirm they exist.
- IDOR is the most common serious bug in real applications and the hardest to catch in review,
  because the vulnerable code looks complete. Add tests that fetch another user's object and expect
  a 404.
- Log authorization failures with the caller, the object and the decision. A burst of 404s for ids
  one user does not own is someone walking the range.

## Key points

- Authentication is not authorization; being signed in does not mean being allowed.
- An object reference the client controls must be checked against the caller on the server.
- Unguessable ids are not a control; the ownership check is.
- Return 404, not 403, so you do not confirm the object exists.
- Make owner-scoping the default in the data layer, and test for the cross-user case.
