"""A small SQLite helper and the people the lab's service knows about.

Every case keeps its data in an in-memory SQLite database, seeded the same way on every run, so the
symptom is identical on every machine. The same user ids run through the chapters: u_1041 and
u_1042 are members, u_1099 is an admin. Names are gender-neutral and made up for the lab.
"""

import sqlite3

# id, email, display name, role, password, api token
PEOPLE: list[tuple[str, str, str, str, str, str]] = [
    ("u_1041", "u_1041@acme.test", "Sam Rivera", "member", "hunter2-correct", "tok_1041_7af3c1"),
    ("u_1042", "u_1042@acme.test", "Alex Chen", "member", "let's-go-42", "tok_1042_2bd9e0"),
    (
        "u_1099",
        "u_1099@acme.test",
        "Admin Account",
        "admin",
        "panther-rooftop-4",
        "tok_1099_ff21aa",
    ),
]


def connect() -> sqlite3.Connection:
    """A private in-memory database, usable from the server thread and the test thread."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def seed_people(conn: sqlite3.Connection) -> None:
    conn.execute(
        "CREATE TABLE users ("
        "id TEXT PRIMARY KEY, email TEXT, display_name TEXT, role TEXT, password TEXT, token TEXT)"
    )
    conn.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", PEOPLE)
    conn.commit()
