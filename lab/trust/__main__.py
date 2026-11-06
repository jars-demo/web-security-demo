"""trust: ten web-application weaknesses, one per chapter, all on 127.0.0.1.

list        every case, its level, and which ones are fixed
run N       run case N and watch the weakness
check N     check your fix: the weakness is gone, and the feature still works
hint N      a nudge, one step at a time
try NAME    run an experiment: inject, exfiltrate, tokens or ssrf
"""

import argparse
import importlib
import sys

from trust.checks import CHECKS
from trust.experiments import EXPERIMENTS

CASES = {
    1: ("case01_sqli", "The quote that rewrote the query"),
    2: ("case02_reflected_xss", "The search box that ran its input"),
    3: ("case03_stored_xss", "The comment that ran on every visit"),
    4: ("case04_idor", "The invoice with someone else's name on it"),
    5: ("case05_access_control", "The admin page with no lock on the door"),
    6: ("case06_csrf", "The form that any site could submit"),
    7: ("case07_mass_assignment", "The profile update that granted admin"),
    8: ("case08_ssrf", "The fetch that reached the metadata service"),
    9: ("case09_path_traversal", "The download that climbed out of its folder"),
    10: ("case10_open_redirect", "The login link that pointed off-site"),
}

LEVELS = {
    1: "Foundations",
    2: "Foundations",
    3: "Foundations",
    4: "Access and identity",
    5: "Access and identity",
    6: "Access and identity",
    7: "Access and identity",
    8: "Server-side and redirects",
    9: "Server-side and redirects",
    10: "Server-side and redirects",
}

HINTS = {
    1: [
        "Look at how the query string is built. Where does the email value end up?",
        "A value only stays data if the database is told it is data. Pasting it into the text "
        "lets a quote end the string and start code.",
        'Pass the values as parameters: execute("... WHERE email = ? AND password = ?", '
        "(email, password)). Let the driver bind them.",
    ],
    2: [
        "Print the page for a search term with a < in it. Where does the term appear?",
        "Output into HTML must be encoded for HTML. The browser cannot tell your markup from the "
        "user's unless you escape theirs.",
        "Escape the term before it goes into the page: html.escape(term). Do it on output, every "
        "time, not on input.",
    ],
    3: [
        "The comment is escaped nowhere. Is the problem where it is saved, or where it is shown?",
        "Store the raw text, but encode it for HTML when you render it. The same body may be shown "
        "in many places, each needing its own encoding.",
        "Wrap each author and body in html.escape() when building the list items.",
    ],
    4: [
        "The handler checks you are signed in. What does it not check about the invoice?",
        "Being signed in is not the same as being allowed to see this row. The owner of the row "
        "has to match the person asking.",
        "Compare the invoice owner with the session user, and return 404 if they differ, so you "
        "do not even confirm the id exists.",
    ],
    5: [
        "Both users reach /admin/users. What is the only thing the handler checks?",
        "Hiding the link is a UI choice. The server must check the role on every request to the "
        "page, because anyone can type the URL.",
        "After loading the session, return 403 unless session.role == 'admin'.",
    ],
    6: [
        "What does the POST require beyond the session cookie? Could another site send the same "
        "request?",
        "The defence is a value the session knows and another site cannot read: a token issued to "
        "the session and required on every state-changing request.",
        "Issue session.csrf on GET /account, and reject the POST unless the submitted csrf matches "
        "the session's.",
    ],
    7: [
        "Print the body the handler receives. Which keys does it turn into column updates?",
        "An allowlist beats a blocklist. Decide which fields a profile edit may change, and ignore "
        "every other key.",
        "Update only columns in a fixed set like {'display_name', 'email'}. Drop role and token.",
    ],
    8: [
        "The handler fetches any host it can resolve. Which hosts should the avatar importer ever "
        "need?",
        "Decide the small set of hosts this feature is for and allow only those. A blocklist of "
        "bad addresses always misses one.",
        "Before fetching, return an error unless the URL host is in ALLOWED.",
    ],
    9: [
        "The name is joined onto the folder and opened. Where can ../ or an absolute path land?",
        "Resolve the final path and confirm it is still inside the reports folder before opening "
        "it. Checking the name for '..' is not enough.",
        "Build the full path, realpath() it, and return 404 unless it starts with the realpath of "
        "the base folder plus a separator.",
    ],
    10: [
        "Print the Location for each next value. Which ones leave the site?",
        "A safe redirect target is a path on this site, not a full URL. // and /\\ and a bare "
        "scheme all send the browser elsewhere.",
        "Allow next only if it starts with a single / and not // or /\\; otherwise redirect to /.",
    ],
}


def module(number: int):
    name = f"cases.{CASES[number][0]}"
    importlib.invalidate_caches()
    return importlib.reload(importlib.import_module(name))


def fixed(number: int) -> bool:
    return all(ok for _, ok in CHECKS[number](module(number)))


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    parser = argparse.ArgumentParser(prog="trust", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    for name in ("run", "check", "hint"):
        sub.add_parser(name).add_argument("n", type=int, choices=CASES, metavar="N")
    sub.add_parser("try").add_argument("name", choices=sorted(EXPERIMENTS))
    args = parser.parse_args()

    if args.command == "list":
        last_level = ""
        for number, (_, title) in CASES.items():
            if LEVELS[number] != last_level:
                last_level = LEVELS[number]
                print(f"\n  {last_level}")
            mark = "fixed" if fixed(number) else ""
            print(f"    {number:2d}  {title:<48} {mark}")
        print()
    elif args.command == "run":
        print(f"case {args.n:02d}: {CASES[args.n][1]}\n")
        module(args.n).run()
    elif args.command == "check":
        results = CHECKS[args.n](module(args.n))
        for label, ok in results:
            print(f"  {'PASS' if ok else 'FAIL'}  {label}")
        print()
        if all(ok for _, ok in results):
            print(f"case {args.n} fixed.")
        else:
            print(f"not yet. Try: uv run python -m trust hint {args.n}")
            raise SystemExit(1)
    elif args.command == "hint":
        for step, hint in enumerate(HINTS[args.n], 1):
            print(f"  {step}. {hint}")
    else:
        EXPERIMENTS[args.name]()


if __name__ == "__main__":
    main()
