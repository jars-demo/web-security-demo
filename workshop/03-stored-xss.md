# The comment that ran on every visit

> A comment is saved as typed and shown as typed. Stored once, it runs in the browser of everyone who opens the page.

**Time:** 22 minutes

## Goal

After this chapter you can tell stored XSS from reflected XSS, explain why the stored kind is worse,
and place the encoding where it belongs so a saved payload is shown, not run.

## The idea

Stored cross-site scripting is the same mechanism as reflected XSS, with one change that makes it
far more dangerous: the payload lives in your database. A reflected attack needs a victim to click
a crafted link. A stored attack needs nothing. The attacker posts once. After that, every person
who opens the page runs the script, in their own session, without clicking anything unusual. One
comment can hit every reader, including staff who open the admin view.

The trap is to think about where the text is saved. It is natural to want to "clean" the comment as
it comes in. But the raw text is fine to store; databases hold bytes, not HTML. The danger appears
only at the moment the text is written into a page. That is where the browser decides whether a
string is content or code, so that is where the encoding has to be.

Encoding on output also survives a truth about real systems: the same stored value is shown in many
places. The comment appears in the page, in a moderation queue, in an email digest, in an API
response rendered by someone else's client. Each of those is a different context with a different
correct encoding. If you "sanitize on input" you have to guess all of them in advance and you only
get one stored form. If you encode on output you encode correctly for each place, every time.

When is cleaning input the right call? When the value is meant to contain some markup, such as a
rich-text comment. Then you do not encode, you sanitize with a vetted HTML sanitizer that parses
the markup and keeps a small safe subset. Writing that yourself with string replacement does not
work; `<scr<script>ipt>` and dozens of other tricks defeat it. For plain text, encode on output and
stop there.

## The case

```text
case 03: The comment that ran on every visit

u_1042 left two comments. Now u_1041 opens the page:

  <li><b>u_1042</b>: Great write-up, thanks.
  <li><b>u_1042</b>: <img src=x onerror=fetch('/x?c='+document.cookie)>
```

```bash
uv run python -m trust run 3
```

The first comment is ordinary. The second is an image tag with an `onerror` handler. It was saved
by one user, u_1042, and it is now served to u_1041, and to everyone else who opens the comments
page. Nobody clicked a crafted link. They opened a normal page.

## Reasoning towards the fix

Open `lab/cases/case03_stored_xss.py`. The POST handler stores the author and body as given, which
is correct. The weakness is in the GET handler that builds the list: it writes each author and body
into an `<li>` as-is. That is the output step, and it is the place to encode.

Wrap both the author and the body in `html.escape` when you build each list item. Leave the stored
data alone. Resist the urge to filter `<script>` out of the incoming body; the payload here is an
image tag, and the next one will be something else. Encode where the page is built and every stored
payload becomes visible text.

## Check your fix

As shipped:

```text
  PASS  a plain comment still shows on the page
  FAIL  a stored <img onerror> is not a live tag
  FAIL  a stored <script> is not a live tag
  FAIL  the stored markup is HTML-escaped instead
```

```bash
uv run python -m trust check 3
```

The feature line proves the fix cannot just drop comment bodies. A real comment still shows. The
three failing lines want stored markup to arrive as escaped text, whatever its shape.

## In production

- Encode on output, in the template, for every place a stored value is shown. Treat the API that
  returns raw values as its own context; the client that renders it is responsible for encoding,
  and you should make that contract explicit.
- If you need rich text, use a maintained sanitizer library and a strict allowlist of tags and
  attributes. Never roll your own with regular expressions.
- A Content Security Policy that forbids inline script turns many stored payloads into dead text
  even when one gets past encoding. Add `object-src 'none'` and a tight `script-src`.
- Stored XSS is found by its reach, not its noise. Review every field that is shown back to other
  users: names, bios, comments, filenames, support tickets.

## Key points

- Stored XSS persists; one post runs in every reader's browser with no click.
- The browser decides content-or-code at render time, so encode at render time.
- One stored value is shown in many contexts; output encoding handles each correctly.
- For rich text, sanitize with a vetted library and an allowlist, never with string replacement.
- A strict Content Security Policy is a strong backstop for the payload you missed.
