from flask import Blueprint, render_template, send_file

images_bp = Blueprint("images", __name__)


@images_bp.route("/image/offline")
def imgoff():
    return send_file("static/images/offline.png")


@images_bp.route("/image/profile")
def imgprof():
    return send_file("static/images/profile.png")
