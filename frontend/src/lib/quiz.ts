// Two questions at the end of every chapter, each with one right answer and the reason behind it.

export type Question = {
  q: string
  options: readonly string[]
  answer: number
  why: string
}

export const QUIZ: Record<string, readonly Question[]> = {
  '01': [
    {
      q: 'Why is a parameterized query safe from injection?',
      options: [
        'It escapes dangerous characters in the value',
        'The value is bound as data, never parsed as query text',
        'It rejects values that contain quotes',
      ],
      answer: 1,
      why: 'The database compiles the query with placeholders, then binds the value. A quote in the value is just a character, not query syntax.',
    },
    {
      q: 'A login strips every quote from the input. Is that a fix?',
      options: [
        'Yes, no quote means no injection',
        'No, it breaks valid inputs and misses other vectors',
        'Only if it also removes semicolons',
      ],
      answer: 1,
      why: 'Stripping quotes corrupts a legitimate password that contains one, and injection has shapes that do not need a quote. Binding removes the question.',
    },
  ],
  '02': [
    {
      q: 'Where does the fix for reflected XSS belong?',
      options: [
        'On input, when the value arrives',
        'On output, when the value is written into the page',
        'In the database layer',
      ],
      answer: 1,
      why: 'The browser decides content-or-code at render time. Encode for the context the value lands in, each time it is written out.',
    },
    {
      q: 'A filter removes the string "<script>" from the search term. Enough?',
      options: [
        'Yes, that is the dangerous tag',
        'No, an image tag with onerror still runs',
        'Only against old browsers',
      ],
      answer: 1,
      why: 'XSS has many shapes beyond <script>. Encoding the special characters neutralises all of them at once; a blocklist of tags never ends.',
    },
  ],
  '03': [
    {
      q: 'Why is stored XSS worse than reflected XSS?',
      options: [
        'It is harder to write',
        'It runs for every visitor with no crafted link',
        'It cannot be encoded away',
      ],
      answer: 1,
      why: 'The payload lives in the database and is served to everyone who opens the page, with no click. Reflected XSS needs a victim to follow a crafted link.',
    },
    {
      q: 'You need to allow some rich-text formatting in comments. What do you use?',
      options: [
        'A regex that strips <script>',
        'A vetted HTML sanitizer with a tag allowlist',
        'html.escape on the whole comment',
      ],
      answer: 1,
      why: 'Rich text means real markup, so you cannot just escape it all. A maintained sanitizer parses the HTML and keeps a safe subset; regexes are defeated by nesting tricks.',
    },
  ],
  '04': [
    {
      q: 'The invoice endpoint checks you are signed in. What is missing?',
      options: [
        'A rate limit',
        'A check that the invoice belongs to you',
        'A stronger session cookie',
      ],
      answer: 1,
      why: 'Authentication is not authorization. The handler must compare the object owner with the caller before returning it.',
    },
    {
      q: 'Why return 404, not 403, for an object that is not yours?',
      options: [
        '404 is the correct HTTP code for forbidden',
        'A 403 confirms the object exists, which leaks information',
        'It is faster',
      ],
      answer: 1,
      why: 'A 403 tells the attacker they found a real id. A 404 reveals nothing: there is simply nothing there for them.',
    },
  ],
  '05': [
    {
      q: 'The admin link is hidden from members. Is the admin page protected?',
      options: [
        'Yes, members cannot see the link',
        'No, anyone can type the URL; the server must check the role',
        'Only if the link is removed from the HTML',
      ],
      answer: 1,
      why: 'Hiding a link is a UI choice. Access control has to run on the server, on every request, from the trusted session.',
    },
    {
      q: 'A member sends X-Role: admin. Should the server honour it?',
      options: [
        'Yes, the header states the role',
        'No, the role must come from the server-side session',
        'Only over HTTPS',
      ],
      answer: 1,
      why: 'Anything the client sends is input from the adversary. The role must be read from the session the server established at sign-in.',
    },
  ],
  '06': [
    {
      q: 'Why can a session cookie not prove a request was intended?',
      options: [
        'Cookies expire too quickly',
        'The browser sends cookies on cross-site requests too',
        'Cookies are not encrypted',
      ],
      answer: 1,
      why: 'A form on another site can trigger a request to your app, and the browser attaches the session cookie. The request looks real to the server.',
    },
    {
      q: 'What makes a CSRF token work?',
      options: [
        'It is long and random',
        'It is tied to the session and a foreign site cannot read it',
        'It is stored in a cookie',
      ],
      answer: 1,
      why: 'The same-origin policy stops another site from reading your page to learn the token, so it cannot forge the request. The server compares it to the session.',
    },
  ],
  '07': [
    {
      q: 'How does mass assignment let a member become an admin?',
      options: [
        'The form shows a role field',
        'The handler writes every field in the body, including role',
        'The database defaults everyone to admin',
      ],
      answer: 1,
      why: 'The request body is attacker-controlled. If the handler binds all of it to the record, the request can carry fields the form never showed.',
    },
    {
      q: 'Why is an allowlist better than blocking the "role" field?',
      options: [
        'It is shorter to write',
        'A blocklist misses the next sensitive field, like token',
        'Allowlists are required by HTTP',
      ],
      answer: 1,
      why: 'You can only block holes you already know about. An allowlist excludes every field you did not name, including ones added later.',
    },
  ],
  '08': [
    {
      q: 'What is the real prize in a server-side request forgery?',
      options: [
        "The attacker's own server",
        "The server's network: internal services and cloud metadata",
        'The user who submitted the URL',
      ],
      answer: 1,
      why: 'Your server can reach internal addresses the user cannot, including the cloud metadata endpoint that hands out credentials. SSRF borrows that position.',
    },
    {
      q: 'Why does a blocklist of bad addresses fail for SSRF?',
      options: [
        'It is slow to evaluate',
        'The space of internal addresses and encodings is open-ended',
        'Blocklists cannot match IP addresses',
      ],
      answer: 1,
      why: 'Loopback, IPv6, decimal encodings, and DNS names that resolve inward all reach the same place. An allowlist of destinations closes the question.',
    },
  ],
  '09': [
    {
      q: 'Why is checking the filename for ".." not enough?',
      options: [
        'It is too slow',
        'An absolute path escapes with no ".." at all',
        '".." is valid in filenames',
      ],
      answer: 1,
      why: 'Joining a folder with an absolute path throws the folder away. Encodings and mixed slashes defeat naive checks too. Decide by the resolved path.',
    },
    {
      q: 'What is the strongest fix for a file download by name?',
      options: [
        'Resolve the path and confirm it stays inside the base folder',
        'Reject names longer than 255 characters',
        'Lowercase the filename',
      ],
      answer: 0,
      why: 'Canonicalise the final path and check it is within the base directory. Better still, map an opaque id to a stored path so there is nothing to traverse.',
    },
  ],
  '10': [
    {
      q: 'Why does an open redirect help an attacker?',
      options: [
        'It slows the server down',
        'The link is on your trusted domain but lands on theirs',
        'It reveals the session cookie',
      ],
      answer: 1,
      why: 'The victim trusts the link because it is your domain and certificate. Your app then bounces them to a look-alike page they never saw in the link.',
    },
    {
      q: 'Which redirect target is safe to honour?',
      options: [
        'Anything that does not start with http',
        'A single leading slash, not // or /\\',
        'Any value on the allowlist of blocked hosts',
      ],
      answer: 1,
      why: '// and /\\ both mean another host, and a bare scheme leaves the site. A path that starts with one slash and is not // or /\\ stays on your site.',
    },
  ],
}
