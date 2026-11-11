import sqlite3
from pathlib import Path

from flask import current_app, g
from werkzeug.security import generate_password_hash

SCHEMA = """
CREATE TABLE IF NOT EXISTS organizations (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, admin_note TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, organization_id INTEGER NOT NULL REFERENCES organizations(id),
    email TEXT UNIQUE NOT NULL, display_name TEXT NOT NULL,
    password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('member', 'admin'))
);
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY, organization_id INTEGER NOT NULL REFERENCES organizations(id),
    title TEXT NOT NULL, description TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Open'
);
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY, ticket_id INTEGER NOT NULL REFERENCES tickets(id),
    author_id INTEGER NOT NULL REFERENCES users(id), body TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS attachments (
    id INTEGER PRIMARY KEY, ticket_id INTEGER NOT NULL REFERENCES tickets(id),
    display_name TEXT NOT NULL, storage_name TEXT NOT NULL
);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON", ())
    return g.db


def close_db(error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def seed_database():
    connection = get_db()
    connection.executescript(SCHEMA)
    if connection.execute("SELECT COUNT(*) FROM users", ()).fetchone()[0]:
        return
    attachment_dir = Path(current_app.config["ATTACHMENT_DIR"])
    attachment_dir.mkdir(parents=True, exist_ok=True)
    with connection:
        connection.executemany("INSERT INTO organizations VALUES (?, ?, ?)", [
            (1, "Northstar Studio", "Internal: renewal budget is 12,000 demo credits."),
            (2, "Harbor Labs", "Internal: project Seabird launches in December. Fictional data."),
        ])
        for row in [
            (1, 1, "alice@northstar.example", "Alice", "member"),
            (2, 1, "maria@northstar.example", "Maria", "admin"),
            (3, 2, "bob@harbor.example", "Bob", "member"),
        ]:
            connection.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
                               (*row[:4], generate_password_hash("ReviewLab-2026!"), row[4]))
        connection.executemany("INSERT INTO tickets(id, organization_id, title, description) VALUES (?, ?, ?, ?)", [
            (1, 1, "Invoice export formatting", "The exported invoice needs a consistent date format."),
            (2, 1, "Team onboarding checklist", "Please add the new support contacts to the onboarding guide."),
            (3, 2, "Private launch plan", "Harbor's internal Seabird launch schedule. Only Harbor members should see this."),
        ])
        connection.execute("INSERT INTO comments(ticket_id, author_id, body) VALUES (?, ?, ?)",
                           (1, 2, "Thanks, Alice. Please attach the sample from the test account."))
        connection.executemany("INSERT INTO attachments VALUES (?, ?, ?, ?)", [
            (1, 1, "invoice-sample.txt", "northstar-invoice.txt"),
            (2, 3, "seabird-launch-plan.txt", "harbor-launch.txt"),
        ])
    (attachment_dir / "northstar-invoice.txt").write_text("Northstar sample invoice. Amount: 120 demo credits.\n")
    (attachment_dir / "harbor-launch.txt").write_text("HARBOR INTERNAL: Seabird launches December 12. Fictional training data.\n")


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        seed_database()
