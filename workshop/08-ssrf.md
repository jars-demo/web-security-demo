# The fetch that reached the metadata service

> The avatar importer takes a URL and the server fetches it. The server sits next to internal services the user cannot reach.

**Time:** 26 minutes

## Goal

After this chapter you can explain server-side request forgery, see why the server's network is the
real prize, and defend a URL-fetching feature with an allowlist instead of a blocklist. Everything
here runs on 127.0.0.1; the "internal" service is a lab stand-in for a cloud metadata endpoint, and
no real host is contacted.

## The idea

Some features take a URL and fetch it on the server: import an avatar from a link, call a webhook,
render a link preview, pull a document. The moment your server makes a request on behalf of a user,
the user borrows your server's position on the network. And your server can reach things the user
cannot: internal admin panels with no login, databases, and, in the cloud, the metadata service at
`169.254.169.254` that hands out credentials to anything that asks from inside the instance.

Server-side request forgery is making that borrowed position do work for the attacker. They give
your importer a URL that points inward, your server dutifully fetches it, and the response, often a
secret, comes back through your feature. The attacker never touches the internal service directly.
Your server is the proxy.

The instinct is a blocklist: refuse `169.254.169.254`, refuse anything with "internal" in it. This
loses, and the `ssrf` experiment measures how badly. You cannot enumerate every internal address.
There is `127.0.0.1` and `localhost` and `[::1]` and `0.0.0.0`; there are DNS names that resolve to
private IPs; there are decimal and hex encodings of the same IP; there is DNS rebinding, where the
name passes your check and then resolves to an internal address a moment later. Every blocklist has
a gap because the space of "bad" is open-ended.

An allowlist closes the question. Decide the small set of hosts this feature legitimately needs, an
avatar CDN, a known partner, and allow only those. Everything else is refused, including the clever
encodings, because they are simply not on the list. For features that must reach arbitrary public
URLs, the allowlist becomes a set of rules instead: resolve the host yourself, reject any address in
a private, loopback or link-local range, pin the connection to the address you checked so DNS cannot
change under you, and never follow redirects into a blocked range.

## The case

```text
case 08: The fetch that reached the metadata service

The importer should only fetch the avatar host. Four URLs go in:

  the allowed image host       -> 200  'PNG'
  the cloud metadata IP        -> 200  'root-token=ssrf_9c12e7f0'
  an internal service by name  -> 200  'root-token=ssrf_9c12e7f0'
  the server's own loopback    -> 200  'root-token=ssrf_9c12e7f0'
```

```bash
uv run python -m trust run 8
```

The first URL is the real job: fetch an image. The other three point at the lab's internal service,
by IP, by name, and by loopback, and each one comes back with a root token. The importer fetched
whatever it was handed.

## Reasoning towards the fix

Open `lab/cases/case08_ssrf.py` and find the `fetch` function. It takes the URL, pulls out the host,
and fetches it against the lab's resolver with no check on which host it is. The module already
defines `ALLOWED`, the set of hosts this feature is for.

Before fetching, reject any host that is not in `ALLOWED`. One check, on the host, before any
connection is made. Do not try to blocklist the metadata IP; the run shows two more ways to the same
secret, and there are many more. Allow the one host the feature needs and refuse the rest.

To see the difference between the two strategies:

```bash
uv run python -m trust try ssrf
```

```text
  Of 6 internal targets, the blocklist lets 3 through and the allowlist lets 0 through.
```

The blocklist in that table blocks the known metadata IP and names containing "internal", and still
lets loopback, IPv6 loopback and another internal host straight through. The allowlist blocks all
six, because none of them is the one allowed host.

## Check your fix

As shipped:

```text
  PASS  the allowed image host is still fetched (got 200)
  FAIL  the cloud metadata IP is blocked (got 200)
  FAIL  the internal host by name is blocked (got 200)
  FAIL  the server's own loopback is blocked (got 200)
```

```bash
uv run python -m trust check 8
```

The passing line keeps the importer working for its real host. The three failing lines reach the
internal service three different ways and expect all three blocked. A fix that only blocks the IP
leaves the other two open.

## In production

- Prefer an allowlist of destination hosts for any server-side fetch. It is the only approach that
  does not have to predict every bad address.
- When arbitrary URLs are required, resolve the host, reject private, loopback, link-local and
  metadata ranges, connect to the resolved address, and do not follow redirects into a blocked
  range. Re-check after every redirect.
- Block the cloud metadata endpoint at the network layer too, and use the hardened metadata service
  (IMDSv2 and equivalents) so a single fetch cannot lift credentials.
- Give the fetcher its own identity with no standing access, and log every outbound URL it is asked
  to fetch. A spike of requests toward internal ranges is the signal.

## Key points

- A server that fetches a user's URL lends the user its network position.
- The prize is the internal network: admin panels, databases, and cloud metadata credentials.
- Blocklists of bad addresses always leak; the encodings and names are open-ended.
- An allowlist of destinations, or strict range-checking with pinned connections, closes it.
- Harden the metadata service and log every outbound fetch.
