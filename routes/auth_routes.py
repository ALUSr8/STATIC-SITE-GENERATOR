import sqlite3

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from modules.auth_service import (
    authenticate_user,
    create_user,
    get_user_by_id,
    mark_tutorial_seen
)

auth_bp = Blueprint(
    "auth",
    __name__
)


def start_user_session(user, show_tutorial=True):

    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["show_tutorial"] = show_tutorial


@auth_bp.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":
        username = request.form.get(
            "username",
            ""
        ).strip()
        password = request.form.get(
            "password",
            ""
        )

        user = authenticate_user(
            username,
            password
        )

        if user is None:
            flash(
                "Invalid username or password."
            )
            return render_template(
                "login.html",
                username=username
            )

        start_user_session(
            user,
            show_tutorial=True
        )

        return redirect(
            url_for(
                "home.home"
            )
        )

    return render_template(
        "login.html"
    )


@auth_bp.route(
    "/signup",
    methods=["GET", "POST"]
)
def signup():

    if request.method == "POST":
        username = request.form.get(
            "username",
            ""
        ).strip()
        password = request.form.get(
            "password",
            ""
        )

        if username == "" or password == "":
            flash(
                "Username and password are required."
            )
            return render_template(
                "signup.html",
                username=username
            )

        if len(username) > 64 or len(password) < 8 or len(password) > 128:
            flash(
                "Use a username up to 64 characters and a password from 8 to 128 characters."
            )
            return render_template(
                "signup.html",
                username=username
            )

        try:
            user_id = create_user(
                username,
                password
            )
        except sqlite3.IntegrityError:
            flash(
                "That username is already taken."
            )
            return render_template(
                "signup.html",
                username=username
            )

        user = get_user_by_id(
            user_id
        )

        start_user_session(
            user,
            show_tutorial=True
        )

        return redirect(
            url_for(
                "home.home"
            )
        )

    return render_template(
        "signup.html"
    )


@auth_bp.route(
    "/logout",
    methods=["POST"]
)
def logout():

    session.clear()
    flash(
        "Signed out."
    )

    return redirect(
        url_for(
            "auth.login"
        )
    )


@auth_bp.route(
    "/tutorial/seen",
    methods=["POST"]
)
def tutorial_seen():

    user_id = session.get("user_id")

    if user_id is not None:
        mark_tutorial_seen(
            user_id
        )

    session["show_tutorial"] = False

    return (
        "",
        204
    )
