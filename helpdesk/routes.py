from functools import wraps
import hmac
import secrets

from flask import Blueprint, abort, current_app, flash, g, redirect, render_template, request, send_from_directory, session, url_for
from markupsafe import Markup
from werkzeug.security import check_password_hash

from .db import get_db

bp = Blueprint("main", __name__)


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


def load_user():
    g.user = None
    if session.get("user_id"):
        g.user = get_db().execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()


def protect_forms():
    if request.method == "POST":
        submitted = request.form.get("csrf_token", "")
        expected = session.get("csrf_token", "")
        if not expected or not hmac.compare_digest(expected, submitted):
            abort(400, "Invalid form token")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)
    return wrapped


def ticket_for_user(ticket_id):
    ticket = get_db().execute(
        "SELECT * FROM tickets WHERE id = ? AND organization_id = ?",
        (ticket_id, g.user["organization_id"]),
    ).fetchone()
    if ticket is None:
        abort(404)
    return ticket


def find_user(email):
    return get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()


@bp.app_template_filter("badge")
def badge(label):
    return Markup('<span class="badge">{}</span>').format(label)


@bp.app_template_filter("comment_html")
def comment_html(body):
    return Markup(body)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = find_user(request.form.get("email", ""))
        if user and check_password_hash(user["password_hash"], request.form.get("password", "")):
            session.clear()
            session["user_id"] = user["id"]
            csrf_token()
            return redirect(url_for("main.tickets"))
        flash("Email or password is incorrect.")
    return render_template("login.html")


@bp.post("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@bp.get("/")
@login_required
def tickets():
    rows = get_db().execute("SELECT * FROM tickets WHERE organization_id = ? ORDER BY id", (g.user["organization_id"],)).fetchall()
    return render_template("tickets.html", tickets=rows, query="")


@bp.get("/tickets/search")
@login_required
def search():
    term = request.args.get("q", "")
    query = f"SELECT * FROM tickets WHERE organization_id = {g.user['organization_id']} AND title LIKE '%{term}%' ORDER BY id"
    rows = get_db().execute(query).fetchall()
    return render_template("tickets.html", tickets=rows, query=term)


@bp.get("/tickets/<int:ticket_id>")
@login_required
def ticket_detail(ticket_id):
    ticket = ticket_for_user(ticket_id)
    comments = get_db().execute(
        "SELECT c.*, u.display_name FROM comments c JOIN users u ON u.id = c.author_id WHERE ticket_id = ? ORDER BY c.id",
        (ticket_id,),
    ).fetchall()
    attachments = get_db().execute("SELECT * FROM attachments WHERE ticket_id = ?", (ticket_id,)).fetchall()
    return render_template("ticket.html", ticket=ticket, comments=comments, attachments=attachments)


@bp.post("/tickets/<int:ticket_id>/comments")
@login_required
def add_comment(ticket_id):
    ticket_for_user(ticket_id)
    body = request.form.get("body", "").strip()
    if not body or len(body) > 4000:
        abort(400, "Comments must contain between 1 and 4000 characters")
    connection = get_db()
    connection.execute("INSERT INTO comments(ticket_id, author_id, body) VALUES (?, ?, ?)", (ticket_id, g.user["id"], body))
    connection.commit()
    return redirect(url_for("main.ticket_detail", ticket_id=ticket_id))


@bp.get("/attachments/<int:attachment_id>")
@login_required
def attachment(attachment_id):
    row = get_db().execute("SELECT * FROM attachments WHERE id = ?", (attachment_id,)).fetchone()
    if row is None:
        abort(404)
    return send_from_directory(current_app.config["ATTACHMENT_DIR"], row["storage_name"],
                               as_attachment=True, download_name=row["display_name"])


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        name = request.form.get("display_name", "").strip()
        role = request.form.get("role", g.user["role"])
        if not name or len(name) > 80 or role not in ("member", "admin"):
            abort(400, "Invalid profile")
        connection = get_db()
        connection.execute("UPDATE users SET display_name = ?, role = ? WHERE id = ?", (name, role, g.user["id"]))
        connection.commit()
        flash("Profile updated.")
        return redirect(url_for("main.profile"))
    return render_template("profile.html")


@bp.get("/admin")
@login_required
def admin():
    if g.user["role"] != "admin":
        abort(403)
    organization = get_db().execute("SELECT * FROM organizations WHERE id = ?", (g.user["organization_id"],)).fetchone()
    members = get_db().execute("SELECT display_name, email, role FROM users WHERE organization_id = ?", (g.user["organization_id"],)).fetchall()
    return render_template("admin.html", organization=organization, members=members)
