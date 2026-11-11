from flask import Flask, abort, g, redirect, request, session, url_for
import hmac
import os
import secrets
from modules.auth_service import get_user_by_id
from routes.auth_routes import auth_bp
from routes.home_routes import home_bp
from routes.builder_routes import builder_bp
from database.db import initialize_database
from routes.project_routes import project_bp
from routes.component_routes import component_bp
from flask import send_from_directory
from routes.theme_routes import theme_bp
from routes.export_routes import export_bp
from routes.preview_routes import preview_bp
from routes.markdown_routes import markdown_bp
from modules.security import safe_link_url, safe_video_url

app = Flask(__name__)


def load_secret_key():
    configured_key = os.environ.get("SECRET_KEY")

    if configured_key:
        return configured_key

    key_path = os.path.join(
        app.root_path,
        "database",
        ".flask_secret_key"
    )

    try:
        with open(key_path, "r", encoding="utf-8") as key_file:
            key = key_file.read().strip()

            if key:
                return key
    except FileNotFoundError:
        pass

    key = secrets.token_urlsafe(48)
    with open(key_path, "w", encoding="utf-8") as key_file:
        key_file.write(key)
    return key


app.secret_key = load_secret_key()
app.config.update(
    CSRF_ENABLED=True,
    MAX_CONTENT_LENGTH=5 * 1024 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE") == "1"
)
app.add_template_filter(safe_link_url, "safe_link_url")
app.add_template_filter(safe_video_url, "safe_video_url")


def csrf_token():
    token = session.get("_csrf_token")

    if token is None:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token

    return token


app.jinja_env.globals["csrf_token"] = csrf_token


@app.before_request
def require_csrf_token():
    if (
        app.config["CSRF_ENABLED"]
        and not app.testing
        and request.method in {"POST", "PUT", "PATCH", "DELETE"}
    ):
        submitted_token = request.form.get(
            "_csrf_token",
            request.headers.get("X-CSRF-Token", "")
        )

        if not hmac.compare_digest(submitted_token, csrf_token()):
            abort(400)
app.config["UPLOAD_FOLDER"] = "user_uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
initialize_database()

PUBLIC_ENDPOINTS = {
    "auth.login",
    "auth.signup",
    "static",
}

app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(builder_bp)
app.register_blueprint(component_bp)
app.register_blueprint(theme_bp)
app.register_blueprint(project_bp)
app.register_blueprint(export_bp)
app.register_blueprint(preview_bp)
app.register_blueprint(markdown_bp)

@app.before_request
def require_login():

    g.current_user = None

    user_id = session.get("user_id")

    if user_id is not None:
        g.current_user = get_user_by_id(
            user_id
        )

    endpoint = request.endpoint

    if (
        endpoint in PUBLIC_ENDPOINTS
        or endpoint == "auth.logout"
        or endpoint == "auth.tutorial_seen"
        or endpoint == "exports.exported_file"
    ):
        return None

    if g.current_user is None:
        return redirect(
            url_for(
                "auth.login"
            )
        )

    return None

@app.route(
    "/uploads/<path:filename>"
)
def uploaded_file(filename):

    return send_from_directory(
        "user_uploads",
        filename
    )

if __name__ == "__main__":
    app.run()
