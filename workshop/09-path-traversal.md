# The download that climbed out of its folder

> The download handler joins a filename onto a folder and opens it. A name with ../ in it reads a file the folder was meant to keep in.

**Time:** 22 minutes

## Goal

After this chapter you can recognise path traversal, explain why checking a name for `..` is not
enough, and confine file access to a base directory by resolving the real path. Everything here
happens inside one temporary folder the lab makes and deletes; no real system file is read.

## The idea

A download handler takes a filename and serves the matching file from a folder. The natural code is
to join the folder and the name and open the result. The problem is that filesystem paths have a
grammar the attacker can speak: `..` means "go up one level". A name like `../secret.key` joined
onto the reports folder resolves to the parent of that folder, outside the area you meant to expose.
An absolute path does worse: joining a folder with an absolute path throws the folder away entirely
and opens the absolute path.

This is path traversal, also called directory traversal. The feature is "serve a file from here",
and the attacker turns it into "serve a file from anywhere the server process can read": config
files, keys, other users' uploads, the application's own source.

The tempting fix is to look at the name and reject it if it contains `..`. This does not hold. An
absolute path contains no `..` and still escapes. Percent-encoding, double-encoding, mixed slashes
and `....//` all defeat naive string checks. The problem is that you are inspecting the input
instead of the result.

The fix is to decide by the resolved path, not the raw name. Join the name onto the base, resolve
the result to an absolute, canonical path (following `..` and symlinks), and then check that the
resolved path is still inside the base directory. If it is not, refuse. You are no longer guessing
which names are dangerous; you are confirming where the path actually points, which is the only
thing that matters.

When is a name check acceptable? As an early, cheap rejection on top of the resolved-path check,
never instead of it. The resolved-path check is the control.

## The case

```text
case 09: The download that climbed out of its folder

The reports folder holds two files. A secret sits one level above it.

  a real report          name='q3-summary.txt'
       -> 200  'Q3 summary: revenue up 4 percent.'
  climb one level up     name='../secret.key'
       -> 200  'signing-key=pt_4d7b2a90'
  an absolute path       name='/tmp/web-security-lab-pt-XXXX/secret.key'
       -> 200  'signing-key=pt_4d7b2a90'
```

```bash
uv run python -m trust run 9
```

The first name is a real report. The second climbs one level with `../` and reads the secret that
sits beside the reports folder. The third gives an absolute path (the lab prints the real temporary
path, which changes each run) and reads the same secret with no `..` at all.

## Reasoning towards the fix

Open `lab/cases/case09_path_traversal.py`. The handler joins `base` and `name` and opens the result.
Nothing checks where that result lands.

Resolve the joined path to its real, absolute form, then confirm it still starts with the real path
of the base folder plus a separator. Refuse otherwise. Build the check on the resolved path, not on
the text of the name. A `..` filter would catch the second case and miss the absolute path; the
resolved-path check catches both.

## Check your fix

As shipped:

```text
  PASS  a real report is still served (got 200)
  FAIL  climbing one level up is blocked (got 200)
  FAIL  an absolute path is blocked (got 200)
  PASS  a deeper climb is blocked (got 404)
```

```bash
uv run python -m trust check 9
```

The check attacks two ways: `../secret.key` and an absolute path to the same secret. A fix that only
bans `..` blocks the first and still fails the absolute path. The real report is still served, so
the fix cannot just refuse everything.

## In production

- Resolve the final path and confirm it is inside the intended base directory before opening it.
  Use the platform's canonical-path function so `..` and symlinks are followed.
- Better still, do not let the client name a file at all. Map an opaque id to a stored path through
  a lookup you control, so there is no path to traverse.
- Serve user files from a dedicated directory, or object storage, with the application process
  holding no read access to anything else it does not need.
- Normalise and decode the name once, then check; and log any request whose resolved path falls
  outside the base. That log line is an attacker probing.

## Key points

- Path grammar lets `..` and absolute paths escape a folder you meant to confine.
- Checking the raw name for `..` misses absolute paths and encodings.
- Decide by the resolved, canonical path, and confirm it stays inside the base.
- Mapping an id to a stored path removes the traversal surface entirely.
- Run the file server with least filesystem access, and log out-of-base requests.
