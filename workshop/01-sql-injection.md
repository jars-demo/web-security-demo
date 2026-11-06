# The quote that rewrote the query

> A login builds its SQL by pasting the email and password into the query string. One quote ends the data and starts code.

**Time:** 25 minutes

## Goal

After this chapter you can spot a query built by string concatenation, explain how one crafted
value turns data into query, and fix it with bound parameters. You will also see why the common
half-fixes, stripping quotes and blocking keywords, do not hold.

## The idea

A SQL query is a program. When you write

```python
query = f"SELECT id, role FROM users WHERE email = '{email}' AND password = '{password}'"
```

you are not passing the email to the database as a value. You are building the text of a program
and letting the database compile it. The database has no way to know which parts you meant as code
and which parts came from a stranger. It just reads the text.

So the attacker writes text. If the email is `x' OR '1'='1' -- `, the single quote closes the
string that was supposed to hold the email, `OR '1'='1'` becomes part of the `WHERE` clause, and
`--` turns the rest of the line, including the password check, into a comment. The query that runs
is not the query you wrote.

The fix is to stop building the program by hand. A parameterized query sends the query text and
the values on separate tracks:

```python
db.execute("SELECT id, role FROM users WHERE email = ? AND password = ?", (email, password))
```

The database compiles the query once, with placeholders, then binds the values into the compiled
plan. A value is only ever a value. A quote inside it is just a character in a string. This is not
escaping, and it is not slower. The `inject` experiment at the end times both and the difference is
noise.

When is the usual advice wrong? "Escape the input" is the advice people reach for, and manual
escaping (doubling every quote) can be made to work, but it is fragile: it depends on the exact
quoting rules of one database, it breaks the moment a value reaches a context you did not escape
for, and it is one forgotten call away from a hole. "Validate the input" helps defence in depth but
is not the fix: plenty of valid emails and passwords contain quotes. Binding is the fix because it
removes the question of which characters are dangerous. None of them are.

## The case

```text
case 01: The quote that rewrote the query

A real sign-in, a wrong password, then two crafted emails:

  u_1041 with the right password     -> 200  u_1041
       sql: SELECT id, role FROM users WHERE email = 'u_1041@acme.test' AND password = 'hunter2-correct'
  u_1041 with a wrong password       -> 401  wrong email or password
       sql: SELECT id, role FROM users WHERE email = 'u_1041@acme.test' AND password = 'nope'
  the OR-always-true email           -> 200  u_1041
       sql: SELECT id, role FROM users WHERE email = 'x' OR '1'='1' -- ' AND password = 'anything'
  sign in as the admin, no password  -> 200  u_1099
       sql: SELECT id, role FROM users WHERE email = 'u_1099@acme.test' -- ' AND password = 'anything'
```

Run it yourself:

```bash
uv run python -m trust run 1
```

Two crafted emails sign in. The first returns the first user in the table with no password at all.
The second names the admin and comments out the password check, so it signs in as the admin
knowing only the admin's email address.

## Reasoning towards the fix

Look at the handler in `lab/cases/case01_sqli.py`. The `email` and `password` values are read from
the form and dropped straight into the query text. Ask the one question that matters: does the
database ever learn that these came from the user? It does not. It only sees finished query text.

So the job is to keep the values off the query text. Find the `db.execute` call and give it a query
with `?` placeholders, then pass the values as the second argument, a tuple. Let the driver bind
them. Do not try to clean the values first; that is solving the wrong problem.

To measure the point rather than take it on faith:

```bash
uv run python -m trust try inject
```

```text
  input                       what it is          built rows      bound rows
  ------------------------    ----------------    ------------    ------------
  u_1041@acme.test            a real sign-in      1 row           1 row
  u_1041@acme.test            a wrong password    0 rows          0 rows
  x' OR '1'='1' --            OR always true      3 rows          0 rows
  u_1099@acme.test' --        comment out the password  1 row           0 rows
```

The same inputs return all three users through the built query and nothing through the bound one.
Binding did not filter the attack. It made the attack an ordinary string that matches no row.

## Check your fix

As shipped, the check fails:

```text
  PASS  u_1041 signs in with the right password (got 200)
  FAIL  u_1042 signs in with a password that has a quote (got 500)
  PASS  a wrong password is refused (got 401)
  FAIL  the OR-always-true email does not sign anyone in (got 200)
  FAIL  a comment payload does not sign in as the admin (got 200)
```

```bash
uv run python -m trust check 1
```

Notice the first failing line. One real user has a quote in their password. The string-built query
does not just let attackers in; it also throws a 500 on a legitimate password that happens to
contain a quote. The same bug that is a hole is also an outage. Binding fixes both: the quote user
signs in, and the two crafted emails are refused.

## In production

- Use the database driver's parameter binding everywhere, including `IN (...)` lists, `LIKE`
  patterns and `ORDER BY`. Column and table names cannot be bound, so pick those from a fixed
  allowlist, never from request data.
- An ORM helps, but raw SQL sneaks back in for reports and migrations. Grep for string formatting
  next to `execute`, `cursor` and `raw` in review and in CI.
- Give the application's database user the narrowest rights it needs. A read endpoint does not need
  `DELETE`. If an injection does land, least privilege decides how far it reaches.
- Log the parameterized query text, never the bound values, so an attacker's payload does not end
  up pasted into your logs. Alert on database errors that spike, which is what blind injection
  probing looks like from the outside.

## Key points

- A query built by concatenation is a program the attacker can help write.
- Bound parameters keep values off the query text, so a quote is only ever a quote.
- Binding is not escaping and is not slower; the measured difference is noise.
- Stripping quotes and blocking keywords both miss cases and break real inputs.
- Least privilege and query-text-only logging limit the blast radius if one slips through.
