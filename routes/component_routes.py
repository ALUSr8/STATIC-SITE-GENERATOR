from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    abort,
    flash
)

from modules.page_service import (
    get_page_by_id
)

from modules.project_service import (
    get_project_by_id
)

from modules.component_service import (
    create_component,
    get_components_by_page,
    get_component_by_id,
    update_component_data,
    update_component_order,
    delete_component
)

from modules.component_definitions import (
    COMPONENT_TYPES
)

from flask import request
from werkzeug.utils import secure_filename
import os
import uuid
from PIL import Image, UnidentifiedImageError
from modules.theme_service import ensure_theme
from modules.security import safe_link_url

component_bp = Blueprint(
    "components",
    __name__
)

UPLOAD_FOLDER = "user_uploads"
ALLOWED_IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "gif",
    "webp"
}

IMAGE_FORMATS = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "gif": "GIF",
    "webp": "WEBP"
}

MAX_IMAGE_PIXELS = 20_000_000

SIZE_OPTIONS = {
    "small",
    "medium",
    "large"
}

ALIGNMENT_OPTIONS = {
    "left",
    "center",
    "right"
}


def selected_size():

    size = request.form.get(
        "size",
        "medium"
    )

    if size not in SIZE_OPTIONS:
        return "medium"

    return size


def selected_alignment(default="center"):

    alignment = request.form.get(
        "alignment",
        default
    )

    if alignment not in ALIGNMENT_OPTIONS:
        return default

    return alignment


def allowed_image(filename):

    safe_name = secure_filename(filename)

    return (
        safe_name != ""
        and "." in safe_name
        and safe_name.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
    )


def unique_upload_name(filename):

    safe_name = secure_filename(
        filename
    )

    extension = os.path.splitext(safe_name)[1].lower()

    return f"{uuid.uuid4().hex}{extension}"


def validate_image(image_file):

    extension = secure_filename(image_file.filename).rsplit(
        ".",
        1
    )[1].lower()

    try:
        image = Image.open(image_file.stream)
        image.verify()
        image_file.stream.seek(0)

        with Image.open(image_file.stream) as verified_image:
            if verified_image.format != IMAGE_FORMATS[extension]:
                raise ValueError("The file content does not match its extension.")

            if verified_image.width * verified_image.height > MAX_IMAGE_PIXELS:
                raise ValueError("Images must be 20 megapixels or smaller.")
    except (Image.DecompressionBombError, UnidentifiedImageError, OSError):
        raise ValueError("Upload a valid JPG, PNG, GIF, or WebP image.")
    finally:
        image_file.stream.seek(0)


def save_uploaded_image(image_file):

    if image_file is None or image_file.filename == "":
        return None

    if not allowed_image(image_file.filename):
        raise ValueError(
            "Only JPG, PNG, GIF, and WebP images are supported."
        )

    validate_image(image_file)

    os.makedirs(
        UPLOAD_FOLDER,
        exist_ok=True
    )

    filename = unique_upload_name(
        image_file.filename
    )

    image_file.save(
        os.path.join(
            UPLOAD_FOLDER,
            filename
        )
    )

    return filename


def require_owned_page(page_id):

    page = get_page_by_id(
        page_id
    )

    if page is None:
        abort(404)

    if get_project_by_id(page["project_id"]) is None:
        abort(404)

    return page


def require_owned_component(component_id):

    component = get_component_by_id(
        component_id
    )

    if component is None:
        abort(404)

    require_owned_page(
        component["page_id"]
    )

    return component

@component_bp.route(
    "/pages/<int:page_id>"
)
def page_editor(page_id):

    page = require_owned_page(
        page_id
    )

    components = get_components_by_page(
        page_id
    )

    theme = ensure_theme(
    page["project_id"]
    )

    return render_template(
    "page_editor.html",
    page=page,
    components=components,
    theme=theme,
    component_types=COMPONENT_TYPES
    )


@component_bp.route(
    "/pages/<int:page_id>/add/<component_type>"
)
def add_component(
    page_id,
    component_type
):

    require_owned_page(
        page_id
    )

    if component_type not in COMPONENT_TYPES:
        abort(400)

    default_data = {}

    if component_type == "hero":

        default_data = {
            "title": "Hero Title",
            "subtitle": "Hero Subtitle",
            "alignment": "center"
        }

    elif component_type == "text":

        default_data = {
            "content": "Sample text"
        }

    elif component_type == "image":

        default_data = {
            "image_path": "",
            "alignment": "center"
        }

    elif component_type == "gallery":

        default_data = {
            "images": [],
            "alignment": "center"
        }

    elif component_type == "features":

        default_data = {
            "heading": "What you get",
            "items": "Fast setup\nResponsive design\nClear calls to action"
        }

    elif component_type == "cta":

        default_data = {
            "headline": "Ready to get started?",
            "button_text": "Contact Us",
            "button_url": "#contact"
        }

    elif component_type == "testimonial":

        default_data = {
            "quote": "This made our page feel polished in minutes.",
            "author": "Happy Client"
        }

    elif component_type == "pricing":

        default_data = {
            "plan": "Starter",
            "price": "$49",
            "features": "One page site\nContact section\nBasic support"
        }

    elif component_type == "contact":

        default_data = {
            "heading": "Contact",
            "email": "hello@example.com",
            "phone": "+1 555 0100",
            "address": "Your city"
        }

    elif component_type == "business_card":

        default_data = {
            "name": "Your Name",
            "role": "Founder",
            "company": "Company Name",
            "email": "hello@example.com",
            "website": "https://example.com"
        }

    elif component_type == "product_demo":

        default_data = {
            "title": "Product Demo",
            "description": "Show the main benefit, workflow, or feature here.",
            "button_text": "Watch Demo",
            "button_url": "#",
            "video_url": ""
        }

    elif component_type == "blog_post":

        default_data = {
            "title": "Blog Post Title",
            "meta": "By Author - June 2026",
            "excerpt": "A short intro that previews the article."
        }

    elif component_type == "portfolio":

        default_data = {
            "title": "Selected Work",
            "summary": "A concise case study or project highlight.",
            "details": "Client: Example\nRole: Design and build\nResult: Launched successfully"
        }

    elif component_type == "footer":

        default_data = {
            "copyright":
            "Copyright 2026"
        }

    default_data["size"] = "medium"

    existing_components = get_components_by_page(
        page_id
    )

    display_order = 1

    if len(existing_components) > 0:
        display_order = max(
            component["display_order"] or 0
            for component in existing_components
        ) + 1

    create_component(
        page_id=page_id,
        component_type=component_type,
        component_data=default_data,
        display_order=display_order
    )

    flash(
        f"{COMPONENT_TYPES[component_type]['name']} added."
    )

    return redirect(
        url_for(
            "components.page_editor",
            page_id=page_id
        )
    )

@component_bp.route(
    "/components/<int:component_id>/edit",
    methods=["GET", "POST"]
)
def edit_component(component_id):

    component = require_owned_component(
        component_id
    )

    if request.method == "POST":

        if component["component_type"] == "hero":

            updated_data = {
                "title":
                request.form["title"],

                "subtitle":
                request.form["subtitle"],

                "alignment":
                selected_alignment("center")
            }

        elif component["component_type"] == "text":

            updated_data = {
                "content":
                request.form["content"]
            }

        elif component["component_type"] == "footer":

            updated_data = {
                "copyright":
                request.form["copyright"]
            }

        elif component["component_type"] == "features":

            updated_data = {
                "heading": request.form["heading"],
                "items": request.form["items"]
            }

        elif component["component_type"] == "cta":

            updated_data = {
                "headline": request.form["headline"],
                "button_text": request.form["button_text"],
                "button_url": safe_link_url(request.form["button_url"])
            }

        elif component["component_type"] == "testimonial":

            updated_data = {
                "quote": request.form["quote"],
                "author": request.form["author"]
            }

        elif component["component_type"] == "pricing":

            updated_data = {
                "plan": request.form["plan"],
                "price": request.form["price"],
                "features": request.form["features"]
            }

        elif component["component_type"] == "contact":

            updated_data = {
                "heading": request.form["heading"],
                "email": request.form["email"],
                "phone": request.form["phone"],
                "address": request.form["address"]
            }

        elif component["component_type"] == "business_card":

            updated_data = {
                "name": request.form["name"],
                "role": request.form["role"],
                "company": request.form["company"],
                "email": request.form["email"],
                "website": safe_link_url(request.form["website"])
            }

        elif component["component_type"] == "product_demo":

            updated_data = {
                "title": request.form["title"],
                "description": request.form["description"],
                "button_text": request.form["button_text"],
                "button_url": safe_link_url(request.form["button_url"]),
                "video_url": safe_link_url(request.form["video_url"], default="")
            }

        elif component["component_type"] == "blog_post":

            updated_data = {
                "title": request.form["title"],
                "meta": request.form["meta"],
                "excerpt": request.form["excerpt"]
            }

        elif component["component_type"] == "portfolio":

            updated_data = {
                "title": request.form["title"],
                "summary": request.form["summary"],
                "details": request.form["details"]
            }

        elif component["component_type"] == "gallery":

            current_images = component["component_data"].get(
                "images",
                []
            )
            alt_text = request.form.get(
                "alt_text",
                ""
            )

            try:
                for image_file in request.files.getlist("images"):
                    filename = save_uploaded_image(
                        image_file
                    )

                    if filename is not None:
                        current_images.append(
                            {
                                "image_path": filename,
                                "alt_text": alt_text
                            }
                        )
            except ValueError as error:
                flash(str(error))
                return redirect(
                    url_for(
                        "components.edit_component",
                        component_id=component_id
                    )
                )

            updated_data = {
                "images": current_images,
                "alignment": selected_alignment("center")
            }

        else:

            updated_data = component[
                "component_data"
            ]

        updated_data["size"] = selected_size()

        update_component_data(
            component_id,
            updated_data
        )

        flash(
            "Component saved."
        )

        return redirect(
            url_for(
                "components.page_editor",
                page_id=component["page_id"]
            )
        )

    return render_template(
        "edit_component.html",
        component=component
    )


@component_bp.route(
    "/components/<int:component_id>/delete",
    methods=["POST"]
)
def remove_component(component_id):

    component = require_owned_component(
        component_id
    )

    page_id = component["page_id"]

    delete_component(
        component_id
    )

    flash(
        "Component deleted."
    )

    return redirect(
        url_for(
            "components.page_editor",
            page_id=page_id
        )
    )


@component_bp.route(
    "/components/<int:component_id>/move/<direction>",
    methods=["POST"]
)
def move_component(component_id, direction):

    component = require_owned_component(
        component_id
    )

    if direction not in {
        "up",
        "down"
    }:
        abort(400)

    components = get_components_by_page(
        component["page_id"]
    )

    current_index = next(
        (
            index
            for index, page_component in enumerate(components)
            if page_component["id"] == component_id
        ),
        None
    )

    if current_index is None:
        abort(404)

    target_index = current_index - 1

    if direction == "down":
        target_index = current_index + 1

    if 0 <= target_index < len(components):
        target_component = components[target_index]

        update_component_order(
            component_id,
            target_component["display_order"]
        )

        update_component_order(
            target_component["id"],
            component["display_order"]
        )

        flash(
            "Component moved."
        )
    else:
        flash(
            "Component is already in that position."
        )

    return redirect(
        url_for(
            "components.page_editor",
            page_id=component["page_id"]
        )
    )


@component_bp.route(
    "/upload-image",
    methods=["GET", "POST"]
)
def upload_image():

    if request.method == "POST":

        image = request.files.get("image")

        if image and image.filename != "":

            try:
                filename = save_uploaded_image(
                    image
                )
            except ValueError as error:
                flash(str(error))
                return redirect(
                    url_for(
                        "components.upload_image"
                    )
                )

            return (
                f"Uploaded: {filename}"
            )

    return render_template(
        "upload_image.html"
    )

@component_bp.route(
    "/components/<int:component_id>/image",
    methods=["GET", "POST"]
)
def edit_image(component_id):

    component = require_owned_component(
        component_id
    )

    if request.method == "POST":

        image_file = request.files.get("image")

        updated_image_path = component["component_data"].get(
            "image_path",
            ""
        )

        try:
            filename = save_uploaded_image(
                image_file
            )
        except ValueError as error:
            flash(str(error))
            return redirect(
                url_for(
                    "components.edit_component",
                    component_id=component_id
                )
            )

        if filename is not None:
            updated_image_path = filename

        update_component_data(
            component_id,
            {
                "image_path": updated_image_path,
                "alt_text": request.form.get(
                    "alt_text",
                    ""
                ),
                "alignment": request.form.get(
                    "alignment",
                    "center"
                ) if request.form.get("alignment") in ALIGNMENT_OPTIONS else component["component_data"].get("alignment", "center"),
                "size": selected_size()
            }
        )

        flash(
            "Image component saved."
        )

        return redirect(
            url_for(
                "components.page_editor",
                page_id=component["page_id"]
            )
        )

    return render_template(
        "edit_component.html",
        component=component
    )
