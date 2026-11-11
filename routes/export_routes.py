import os

from flask import Blueprint, abort, render_template, send_from_directory, url_for

from modules.export_service import export_project
from modules.project_service import get_project_by_id


export_bp = Blueprint(
    "exports",
    __name__
)


@export_bp.route(
    "/projects/<int:project_id>/export"
)
def export_project_route(project_id):

    project = get_project_by_id(
        project_id
    )

    if project is None:
        abort(404)

    export_folder = export_project(
        project
    )

    export_name = os.path.basename(
        export_folder
    )

    export_url = url_for(
        "exports.exported_file",
        filename=f"{export_name}/index.html"
    )

    return render_template(
        "export_open.html",
        export_url=export_url,
        export_folder=os.path.abspath(export_folder)
    )


@export_bp.route(
    "/exports/<path:filename>"
)
def exported_file(filename):

    return send_from_directory(
        os.path.abspath("exports"),
        filename
    )
