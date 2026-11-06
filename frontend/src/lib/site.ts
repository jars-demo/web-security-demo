// Facts shown on the site. Case titles come from the lab (lab/trust/__main__.py), the symptoms from
// `uv run python -m trust run N`, and the measured numbers from the experiments. Unit tests in
// tests/unit/site.test.ts keep them in step with the lab.

export const REPO_URL = 'https://github.com/jars-demo/web-security-demo'
export const PREV_REPO_URL = 'https://github.com/jars-demo/how-systems-talk-demo'
export const SITE_URL = 'https://websecurity.jishanahmed.in'
export const TITLE = 'Trust no request'
export const SERIES = 'Security series'
export const STAGE = 2
export const TAGLINE =
  'Stage 2 of a hands-on security series. One small Python service on your own machine, ten real web weaknesses, and a check that proves each fix: SQL injection, XSS, CSRF, IDOR, broken access control, SSRF, path traversal, mass assignment and open redirects.'

export type Level = 'Foundations' | 'Access and identity' | 'Server-side and redirects'

export type Case = {
  number: string
  title: string
  topic: string
  level: Level
  symptom: string
}

export const CASES: readonly Case[] = [
  {
    number: '01',
    title: 'The quote that rewrote the query',
    topic: 'SQL injection',
    level: 'Foundations',
    symptom: 'One crafted email signs in as the admin with no password: 200, user u_1099.',
  },
  {
    number: '02',
    title: 'The search box that ran its input',
    topic: 'Reflected XSS',
    level: 'Foundations',
    symptom: 'A <script> in the query comes straight back in the page, ready to run.',
  },
  {
    number: '03',
    title: 'The comment that ran on every visit',
    topic: 'Stored XSS',
    level: 'Foundations',
    symptom: 'A saved comment carries an onerror payload that runs for every later visitor.',
  },
  {
    number: '04',
    title: "The invoice with someone else's name on it",
    topic: 'IDOR',
    level: 'Access and identity',
    symptom: "u_1041 reads u_1042's confidential invoice by changing the number in the URL.",
  },
  {
    number: '05',
    title: 'The admin page with no lock on the door',
    topic: 'Broken access control',
    level: 'Access and identity',
    symptom: 'A member gets the admin user list, with every API token, by typing the URL.',
  },
  {
    number: '06',
    title: 'The form that any site could submit',
    topic: 'CSRF',
    level: 'Access and identity',
    symptom: 'A forged POST with no token changes the account email to attacker@evil.test.',
  },
  {
    number: '07',
    title: 'The profile update that granted admin',
    topic: 'Mass assignment',
    level: 'Access and identity',
    symptom: 'A display-name edit that also sends role=admin makes a member an admin.',
  },
  {
    number: '08',
    title: 'The fetch that reached the metadata service',
    topic: 'SSRF',
    level: 'Server-side and redirects',
    symptom: 'The avatar importer fetches an internal URL and returns a root token.',
  },
  {
    number: '09',
    title: 'The download that climbed out of its folder',
    topic: 'Path traversal',
    level: 'Server-side and redirects',
    symptom: 'A name of ../secret.key reads a file beside the reports folder.',
  },
  {
    number: '10',
    title: 'The login link that pointed off-site',
    topic: 'Open redirect',
    level: 'Server-side and redirects',
    symptom: 'A trusted login link with next=//acme.evil.test redirects the user off-site.',
  },
]

export const LEVELS: readonly { name: Level; blurb: string }[] = [
  {
    name: 'Foundations',
    blurb: 'Untrusted input becomes code: injection and cross-site scripting.',
  },
  {
    name: 'Access and identity',
    blurb: 'Who may touch what: object and function access, forged requests, over-posting.',
  },
  {
    name: 'Server-side and redirects',
    blurb: 'The server acting on a request: its network, its files, and where it sends you.',
  },
]

export const STAGES = [
  { number: 1, name: 'How systems talk', current: false },
  { number: 2, name: 'Trust no request', current: true },
] as const

/** Measured by the lab's experiments on the machine it was written on. Deterministic figures only;
 *  tie-checked against the lab in tests/unit/site.test.ts. */
export const MEASURED = [
  {
    label: 'Tokens dumped through the login',
    value: '3',
    detail: 'every user token recovered in 3 requests and 581 bytes (try exfiltrate)',
  },
  {
    label: 'Rows a string-built query leaks',
    value: '3 of 3',
    detail: 'the OR-always-true email returns every user; bound parameters return 0 (try inject)',
  },
  {
    label: 'Collisions in 200,000 weak tokens',
    value: '142,144',
    detail: 'a predictable scheme repeats; token_urlsafe(24) repeats 0 times (try tokens)',
  },
  {
    label: 'Internal URLs a blocklist lets through',
    value: '3 of 6',
    detail: 'an allowlist lets 0 of 6 through on the same URLs (try ssrf)',
  },
] as const

export const QUICKSTART = `git clone https://github.com/jars-demo/web-security-demo.git
cd web-security-demo/lab
uv sync
uv run python -m trust run 1`
