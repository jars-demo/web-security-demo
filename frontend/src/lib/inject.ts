// The home-page simulator's logic: a tiny login that you can attack. It models the one idea behind
// chapter 01, the difference between building a query from text and binding values as parameters.
// Everything here is pure and unit-tested in tests/unit/inject.test.ts. The user ids and emails are
// the lab's (lab/trust/store.py), and the row counts match `uv run python -m trust try inject`.

export type Mode = 'concat' | 'parameterized'

export type User = { id: string; email: string; password: string }

// The same three people the lab knows, so the simulator and the lab agree.
export const USERS: readonly User[] = [
  { id: 'u_1041', email: 'u_1041@acme.test', password: 'hunter2-correct' },
  { id: 'u_1042', email: 'u_1042@acme.test', password: 'let the dog out' },
  { id: 'u_1099', email: 'u_1099@acme.test', password: 'panther-rooftop-4' },
]

export type Outcome = {
  query: string // the SQL text, with the values shown where they land
  rows: string[] // the ids the query returns
  signedInAs: string | null // the first row's id, or null
  bypass: boolean // signed in without a matching email and password
  error: boolean // the built query is not valid SQL
}

/** Strip a trailing `-- ...` line comment, the way a database would. */
function dropComment(sql: string): string {
  const at = sql.indexOf('--')
  return at === -1 ? sql : sql.slice(0, at)
}

type Term = (user: User) => boolean

/** Parse one comparison: `col = 'lit'` or `'lit' = 'lit'`. Throws on anything else. */
function parseTerm(raw: string): Term {
  const colEq = /^\s*(\w+)\s*=\s*'([^']*)'\s*$/.exec(raw)
  if (colEq) {
    const [, column, literal] = colEq
    return (user: User) => String(user[column as keyof User] ?? '') === literal
  }
  const litEq = /^\s*'([^']*)'\s*=\s*'([^']*)'\s*$/.exec(raw)
  if (litEq) {
    const [, left, right] = litEq
    return () => left === right
  }
  throw new Error(`cannot parse: ${raw}`)
}

/** Evaluate a WHERE body of terms joined by AND and OR (AND binds tighter). */
function evaluate(where: string, user: User): boolean {
  return where
    .split(/\s+OR\s+/i)
    .some((group) => group.split(/\s+AND\s+/i).every((term) => parseTerm(term)(user)))
}

function isRealCredential(email: string, password: string): boolean {
  return USERS.some((u) => u.email === email && u.password === password)
}

/** Run the login with the given email and password, in one of the two modes. */
export function login(email: string, password: string, mode: Mode): Outcome {
  if (mode === 'parameterized') {
    const query =
      'SELECT id FROM users WHERE email = ? AND password = ?  -- bound: [email, password]'
    const rows = USERS.filter((u) => u.email === email && u.password === password).map((u) => u.id)
    return {
      query,
      rows,
      signedInAs: rows[0] ?? null,
      bypass: false,
      error: false,
    }
  }

  const query = `SELECT id FROM users WHERE email = '${email}' AND password = '${password}'`
  try {
    const where = dropComment(query).replace(/^SELECT id FROM users WHERE\s+/i, '')
    const rows = USERS.filter((u) => evaluate(where, u)).map((u) => u.id)
    return {
      query,
      rows,
      signedInAs: rows[0] ?? null,
      bypass: rows.length > 0 && !isRealCredential(email, password),
      error: false,
    }
  } catch {
    return { query, rows: [], signedInAs: null, bypass: false, error: true }
  }
}

// The payloads offered in the simulator, each a real way people attack a string-built login.
export const PRESETS: readonly { label: string; email: string; password: string }[] = [
  { label: 'A real sign-in', email: 'u_1041@acme.test', password: 'hunter2-correct' },
  { label: 'A wrong password', email: 'u_1041@acme.test', password: 'guessing' },
  { label: 'OR always true', email: "x' OR '1'='1' -- ", password: 'anything' },
  { label: 'Sign in as the admin', email: "u_1099@acme.test' -- ", password: 'anything' },
]
