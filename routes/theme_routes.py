from flask import (
    abort,
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from modules.theme_service import (
    ensure_theme,
    update_theme
)
from modules.project_service import (
    get_project_by_id
)

theme_bp = Blueprint(
    "themes",
    __name__
)

@theme_bp.route(
    "/projects/<int:project_id>/theme",
    methods=["GET", "POST"]
)
def edit_theme(project_id):

    if get_project_by_id(project_id) is None:
        abort(404)

    theme = ensure_theme(project_id)

    if request.method == "POST":

        update_theme(
            project_id,
            request.form["font_family"],
            request.form["primary_color"],
            request.form["secondary_color"],
            request.form["background_color"],
            request.form["text_color"]
        )

        flash(
            "Theme saved."
        )

        return redirect(
            url_for(
                "themes.edit_theme",
                project_id=project_id
            )
        )

    return render_template(
        "theme_editor.html",
        project_id=project_id,
        theme=theme
    )
