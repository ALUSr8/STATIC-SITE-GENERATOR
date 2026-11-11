from flask import Blueprint, render_template

builder_bp = Blueprint("builder", __name__)

@builder_bp.route("/builder")
def builder():
    return render_template("builder.html")
