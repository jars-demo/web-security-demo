# Writing a chapter

Each chapter is a Markdown file named `NN-slug.md`, one per lab case, for example `01-sql-injection.md`.
The site reads every file that matches that pattern; this README is ignored.

## Shape

```markdown
# Chapter title

> One or two sentences: the idea of the chapter.

**Time:** 20 minutes

## Goal
## The idea
## The case
## Reasoning towards the fix
## Check your fix
## In production
## Key points
```

- `## The case` quotes the real output of `uv run python -m trust run N`.
- `## Check your fix` quotes the real output of `uv run python -m trust check N` as shipped.
- Both command strings must appear in the chapter: the site's tests look for them.
- Plain English, short sentences, no em dashes.

## The cases

| # | Case file | Chapter file |
| --- | --- | --- |
| 01 | `lab/cases/case01_sqli.py` | `01-sql-injection.md` |
| 02 | `lab/cases/case02_reflected_xss.py` | `02-reflected-xss.md` |
| 03 | `lab/cases/case03_stored_xss.py` | `03-stored-xss.md` |
| 04 | `lab/cases/case04_idor.py` | `04-idor.md` |
| 05 | `lab/cases/case05_access_control.py` | `05-access-control.md` |
| 06 | `lab/cases/case06_csrf.py` | `06-csrf.md` |
| 07 | `lab/cases/case07_mass_assignment.py` | `07-mass-assignment.md` |
| 08 | `lab/cases/case08_ssrf.py` | `08-ssrf.md` |
| 09 | `lab/cases/case09_path_traversal.py` | `09-path-traversal.md` |
| 10 | `lab/cases/case10_open_redirect.py` | `10-open-redirect.md` |
