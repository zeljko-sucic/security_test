import hashlib
import os
from pathlib import Path
import secrets

from flask import Flask

from . import db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=str(Path(app.instance_path) / "helpdesk.sqlite3"),
        ATTACHMENT_DIR=str(Path(app.instance_path) / "attachments"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,
        MAX_CONTENT_LENGTH=64 * 1024,
    )
    if test_config:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    if not app.config.get("SECRET_KEY"):
        secret_file = Path(app.instance_path) / "session.key"
        try:
            fd = os.open(secret_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(fd, "w") as stream:
                stream.write(secrets.token_hex(32))
        app.config["SECRET_KEY"] = secret_file.read_text().strip()
    db.init_app(app)
    from .routes import bp, csrf_token, load_user, protect_forms
    app.register_blueprint(bp)
    app.before_request(load_user)
    app.before_request(protect_forms)
    app.jinja_env.globals["csrf_token"] = csrf_token

    # Cache-busting identifier for the stylesheet; not a session or integrity token.
    stylesheet = Path(app.static_folder) / "style.css"
    asset_version = hashlib.md5(stylesheet.read_bytes(), usedforsecurity=False).hexdigest()[:12]
    app.jinja_env.globals["asset_version"] = asset_version
    return app
