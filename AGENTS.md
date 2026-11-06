# AGENTS.md

Guidance for AI coding agents and developers. Humans: start with [README.md](README.md).

## What this is

"Trust no request", stage 2 of a security series. `lab/` holds ten web-application cases and their
checks; `workshop/` the chapters; `frontend/` the site. Stage 1 is
[How systems talk](https://github.com/jars-demo/how-systems-talk-demo).

## Map

```text
lab/cases/caseNN_*.py        one weakness each; build() returns the app, run() shows the symptom
lab/trust/http.py            a tiny HTTP stack and client, all on 127.0.0.1
lab/trust/store.py           the in-memory SQLite seed (users u_1041, u_1042, admin u_1099)
lab/trust/session.py         a correct session store for the cases that need a signed-in user
lab/trust/checks.py          check_NN(module) -> [(label, ok)]; the feature must still work
lab/trust/experiments.py     trust try inject | exfiltrate | tokens | ssrf
lab/tests/                   cases fail as shipped, pass with tests/solutions/, wrong fixes rejected
frontend/src/lib/site.ts     case titles, symptoms and measured numbers; tests tie them to the lab
frontend/src/lib/inject.ts   the home-page simulator's logic, unit-tested
frontend/src/lib/experiments every measured figure, as the real output it came from
```

## Commands

```bash
cd lab && uv sync && uv run pytest && uv run ruff check . && uv run ruff format --check .
cd frontend && npm ci && npm run verify
```

For the browser tests: `cd frontend && npm run build && npx next start -p 3114`, then
`E2E_BASE_URL=http://localhost:3114 npx playwright test`. Never port 3000.

## Rules

1. **Local only.** Every case runs on 127.0.0.1 against code in this repo. Nothing reaches out. The
   SSRF case's "internal" service is a lab stand-in on loopback; no real host is contacted.
2. **The weaknesses are the product.** Change a case, its check and its solution together.
3. **Checks test the goal.** The feature must still work, so turning it off is never a fix. A
   wrong-fixes test proves the check rejects plausible non-fixes.
4. **Standard library only** in `lab/`. Exact, pinned versions in `frontend/`; new dependencies get
   an exact version at least 14 days old.
5. **Every number is real.** Figures in the chapters and on the site come from real runs. Unit tests
   tie the site's numbers to the lab.
6. **Writing style.** Plain English, short sentences, no em dashes. Gender-neutral example users.
   Conventional Commits, no AI attribution.

## The frontend is Next.js 16

This is not the Next.js in your training data. Read `frontend/AGENTS.md` and the docs under
`frontend/node_modules/next/dist/docs/` before writing framework code.
