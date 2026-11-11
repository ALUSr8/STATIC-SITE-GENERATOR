from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    abort,
    flash
)

from modules.project_service import (
    get_all_projects,
    create_project,
    get_project_by_id,
    delete_project
)
from modules.page_service import (
    delete_page,
    get_page_by_id,
    get_pages_by_project,
    create_page_with_unique_slug
)
project_bp = Blueprint(
    "projects",
    __name__
)


@project_bp.route("/projects")
def projects():

    all_projects = get_all_projects()

    return render_template(
        "projects.html",
        projects=all_projects
    )

@project_bp.route(
    "/projects/new",
    methods=["GET", "POST"]
)
def new_project():

    if request.method == "POST":

        project_name = request.form[
            "project_name"
        ]

        project_description = request.form[
            "project_description"
        ]

        create_project(
            project_name,
            project_description
        )

        flash(
            "Project created. A home page and default theme were added."
        )

        return redirect(
            url_for(
                "projects.projects"
            )
        )

    return render_template(
        "new_project.html"
    )

@project_bp.route("/projects/<int:project_id>")
def project_detail(project_id):

    project = get_project_by_id(
        project_id
    )

    if project is None:
        abort(404)

    pages = get_pages_by_project(
        project_id
    )

    return render_template(
        "project_detail.html",
        project=project,
        pages=pages
    )


@project_bp.route(
    "/projects/<int:project_id>/delete",
    methods=["POST"]
)
def remove_project(project_id):

    project = get_project_by_id(
        project_id
    )

    if project is None:
        abort(404)

    delete_project(
        project_id
    )

    flash(
        "Project deleted."
    )

    return redirect(
        url_for(
            "projects.projects"
        )
    )

@project_bp.route(
    "/projects/<int:project_id>/pages/new",
    methods=["POST"]
)
def new_page(project_id):

    project = get_project_by_id(
        project_id
    )

    if project is None:
        abort(404)

    page_title = request.form.get(
        "page_title",
        ""
    ).strip()

    if page_title == "":
        flash(
            "Page title is required."
        )
        return redirect(
            url_for(
                "projects.project_detail",
                project_id=project_id
            )
        )

    slug = create_page_with_unique_slug(
        project_id,
        page_title
    )

    flash(
        f"Page created with slug '{slug}'."
    )

    return redirect(
        url_for(
            "projects.project_detail",
            project_id=project_id
        )
    )


@project_bp.route(
    "/projects/<int:project_id>/pages/<int:page_id>/delete",
    methods=["POST"]
)
def remove_page(project_id, page_id):

    project = get_project_by_id(
        project_id
    )

    if project is None:
        abort(404)

    page = get_page_by_id(
        page_id
    )

    if page is None or page["project_id"] != project_id:
        abort(404)

    pages = get_pages_by_project(
        project_id
    )

    if len(pages) <= 1:
        flash(
            "A project needs at least one page."
        )
        return redirect(
            url_for(
                "projects.project_detail",
                project_id=project_id
            )
        )

    delete_page(
        page_id
    )

    flash(
        f"Page '{page['title']}' deleted."
    )

    return redirect(
        url_for(
            "projects.project_detail",
            project_id=project_id
        )
    )
