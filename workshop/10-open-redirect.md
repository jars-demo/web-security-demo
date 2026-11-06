# The login link that pointed off-site

> After sign-in the app sends you where you were going, taken from the next parameter. The handler redirects anywhere, including off-site.

**Time:** 22 minutes

## Goal

After this chapter you can recognise an open redirect, explain why it turns your trusted domain into
a launchpad for phishing, and confine a redirect target to your own site. This is also the last
chapter, so it ends with a ten-point production checklist for the whole workshop.

## The idea

Many flows send the user onward after an action: sign in and go back to the page you wanted, follow
a short link, leave and come back. The destination often rides in a parameter like `next` or
`return_to`, and the handler issues a redirect to whatever it holds. If the handler does not check
that value, it will redirect anywhere, including another site.

That is an open redirect, and the damage is trust transfer. The link the victim sees and clicks is
on your real domain, with your real certificate. They trust it, because it is you. Your app then
bounces them to an attacker's page that looks like your login. The victim never saw the attacker's
domain in the link they clicked. Open redirects also chain into worse bugs: they smuggle past URL
allowlists, they turn into token theft when the redirect carries a code or fragment, and they make
OAuth flows leak.

The naive guards all miss. Block anything starting with `http` and the attacker uses
`//evil.test`, which a browser reads as a protocol-relative URL to another host. Block `//` and
they use a backslash, `/\evil.test`, which some browsers normalise to `//`. Block a known bad host
and they pick another. Each guard bans one spelling of "leave the site" and leaves the others.

The fix is to describe what a safe target looks like, not what an unsafe one looks like. A safe
target is a path on your own site: it starts with a single `/`, and it is not `//` or `/\`, which
both mean another host. Anything else falls back to a fixed, safe default like the home page. If you
must redirect to other sites, keep an allowlist of exact destinations and match against it. As with
the other cases, you are naming the small set of good values instead of chasing the open-ended set
of bad ones.

## The case

```text
case 10: The login link that pointed off-site

Sign-in redirects to next. Five values, same trusted login link:

  a page on the site       next='/invoices'
       -> 302  Location: '/invoices'
  a full off-site URL      next='https://acme.evil.test/phish'
       -> 302  Location: 'https://acme.evil.test/phish'
  protocol-relative        next='//acme.evil.test/phish'
       -> 302  Location: '//acme.evil.test/phish'
  backslash trick          next='/\\acme.evil.test/phish'
       -> 302  Location: '/\\acme.evil.test/phish'
  scheme with no slashes   next='https:acme.evil.test'
       -> 302  Location: 'https:acme.evil.test'
```

```bash
uv run python -m trust run 10
```

The first value is a real in-site destination. The other four are four different spellings of "go to
the attacker's host", and the handler sends the browser to each of them from a link that was, in the
address bar, your site.

## Reasoning towards the fix

Open `lab/cases/case10_open_redirect.py`. The handler takes `next` and puts it straight into the
`Location` header. The fix is to accept only a local path.

Allow `next` only when it starts with a single `/` and is not `//` or `/\`; otherwise fall back to
`/`. That one rule keeps the four off-site spellings out while letting a real in-site path through.
Do not block by prefix like `http`; the run shows three ways around that.

## Check your fix

As shipped:

```text
  PASS  a local path is still used as the target (got '/invoices')
  FAIL  a full off-site URL is not used (got 'https://acme.evil.test/phish')
  FAIL  a protocol-relative URL is not used (got '//acme.evil.test/phish')
  FAIL  a backslash trick is not used (got '/\\acme.evil.test/phish')
  FAIL  a scheme with no slashes is not used (got 'https:acme.evil.test')
```

```bash
uv run python -m trust check 10
```

The passing line keeps the real redirect working: an in-site path is still honoured. The four
failing lines are four spellings of leaving the site, and the fix has to turn all of them into the
safe default.

## In production

- Confine redirect targets to local paths, or to an allowlist of exact external destinations. Fall
  back to a safe default, never to the raw value.
- Avoid putting full URLs in redirect parameters at all. Prefer a short key that maps to a known
  path on the server.
- In OAuth and SSO, treat `redirect_uri` as the highest-value allowlist you own; exact-match it,
  including path.
- Log redirects whose target was rejected and fell back. A stream of off-site `next` values is a
  phishing campaign using your domain.

## A ten-point production checklist

You have fixed ten weaknesses. Here is how to keep them fixed across a real codebase:

1. Bind every SQL value as a parameter; pick table and column names from an allowlist, never from
   the request.
2. Encode on output for the context (HTML, attribute, script, URL), and prefer an auto-escaping
   template engine.
3. Sanitize rich text with a vetted library and a tag allowlist; never with string replacement.
4. Scope every read and write by the current user, ideally in the query, and return 404 for objects
   they may not see.
5. Enforce authorization on the server for every route, deny-by-default, from the trusted session,
   never from client input.
6. Require a per-session CSRF token on every state-changing request, and keep safe methods free of
   side effects.
7. Bind request bodies to an explicit allowlist of fields; keep role, token and ownership off the
   general update path.
8. Allowlist destinations for any server-side fetch; range-check and pin connections when arbitrary
   URLs are unavoidable, and harden the metadata service.
9. Confine file access to a base directory by the resolved path, or map opaque ids to stored paths
   so there is nothing to traverse.
10. Confine redirects to local paths or an exact allowlist, set security headers and `SameSite`
    cookies, run with least privilege, and log every authorization failure, blocked fetch and
    rejected redirect.

## Key points

- An unchecked redirect target turns your trusted domain into a phishing launchpad.
- Prefix blocklists miss `//`, `/\` and bare-scheme spellings; describe the safe shape instead.
- Allow a single leading `/` (not `//` or `/\`), or an exact external allowlist, and default safe.
- In OAuth, exact-match `redirect_uri` including the path.
- Every case in this workshop has the same shape: name the small set of good values, not the open
  set of bad ones.
