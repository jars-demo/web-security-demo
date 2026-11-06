# The search box that ran its input

> The search page writes your query back into the HTML. A query made of markup is sent to the next visitor as markup.

**Time:** 22 minutes

## Goal

After this chapter you can explain reflected cross-site scripting, say exactly where the fix
belongs (on output, not input), and encode a value for the HTML context so the browser shows it
instead of running it.

## The idea

A browser builds a page from text. When your server writes

```python
page = f"<p>You searched for: {term}</p>"
```

the `term` becomes part of that text. If the term is `<script>steal()</script>`, the browser does
not see a search term with pointy brackets. It sees a script element, and it runs it. The server
handed the browser markup, so the browser built markup.

Reflected XSS is the version where the payload is not stored. It travels in the request, usually in
a query string, and bounces straight back in the response. The attack is a link. Send someone a
link to the real site with a crafted `q=` on the end, and when they click it the real site reflects
your script into their page, in their session, with their cookies.

The fix is output encoding. Before a value goes into HTML, turn the characters that mean something
in HTML into their harmless forms: `<` becomes `&lt;`, `>` becomes `&gt;`, `&` becomes `&amp;`.
Python's `html.escape` does this. The browser then shows the text `<script>` on the page and runs
nothing.

The key word is context. Encoding is not one thing; it depends on where the value lands. A value
inside element text needs HTML encoding. A value inside an attribute needs attribute encoding and
quoting. A value inside a `<script>` block or a URL needs something else again. "Escape the input
when it arrives" is the advice that sounds safe and is wrong, because the input does not know yet
which context it will land in, and a value is often shown in several places. Encode on output,
each time, for the context it is going into. Templating engines that auto-escape do this for you,
which is the real reason to use one.

## The case

```text
case 02: The search box that ran its input

A normal search, then a search for a script tag:

  plain term 'revenue':
       You searched for: revenue
  a <script> payload:
       You searched for: <script>fetch('/steal?c='+document.cookie)</script>
  an <img onerror> payload:
       You searched for: "><img src=x onerror=alert(document.domain)>
```

```bash
uv run python -m trust run 2
```

The script tag and the image tag come back in the page exactly as typed. In a real browser the
first would send the visitor's cookie to another site, and the second would run when the broken
image failed to load.

## Reasoning towards the fix

Open `lab/cases/case02_reflected_xss.py`. The search term is put into the page with an f-string.
The document titles in the list are fixed strings you control, so they are not the problem. The
`term` is the only untrusted value, and it goes into element text.

So encode it for that context on the way out. Import `html.escape` and wrap the term where it is
written into the page. Do not try to detect or strip `<script>`; the image payload has no script
tag at all, and an attacker has many more shapes than you can list. Encode the dangerous
characters and every shape becomes inert text at once.

## Check your fix

As shipped:

```text
  PASS  a plain search term still shows in the page
  PASS  a matching document is still listed
  FAIL  a <script> payload is not written as a live tag
  FAIL  the script payload is HTML-escaped instead
  FAIL  an <img onerror> payload is not written as a live tag
```

```bash
uv run python -m trust check 2
```

The two passing lines matter as much as the failing ones. The fix has to keep the search working:
a plain term still appears, and a match is still listed. A fix that stops reflecting the term would
pass the security lines and fail the feature. Encoding keeps the feature and removes the weapon.

## In production

- Prefer a templating engine that auto-escapes by default, and learn where it does not: `safe`
  filters, raw blocks, and values put into attributes, inline script or `href`.
- Set a Content Security Policy. It does not replace encoding, but it is a strong second line: a
  good policy can stop an injected inline script from running even if one slips in.
- Reflected XSS loves error pages, search, and anything that echoes a parameter "for convenience".
  Audit every place a request value appears in a response.
- Watch for requests whose parameters contain `<`, `>` or `onerror=`. They are not proof of a hole,
  but a spike of them is someone looking for one.

## Key points

- The browser builds whatever text the server sends; untrusted text becomes untrusted markup.
- Reflected XSS bounces a payload from the request straight into the response, carried by a link.
- Encode on output, for the context the value lands in, not on input.
- No blocklist of tags is complete; encoding the special characters neutralises every shape.
- A Content Security Policy is a valuable second layer, not a substitute for encoding.
