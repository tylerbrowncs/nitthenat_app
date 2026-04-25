from flask import Blueprint, render_template, send_file

images_bp = Blueprint("images", __name__)


@images_bp.route("/image/offline")
def imgoff():
    return send_file("static/images/offline.png")

@images_bp.route("/image/profile")
def imgprof():
    return send_file("static/images/profile.png")

@images_bp.route("/image/tmlogo")
def tmlogo():
    return send_file("static/images/TMLogo.png")

@images_bp.route("/image/tmtablebackground")
def tmbkgrtable():
    return send_file("static/images/TMTableBackground.png")

@images_bp.route("/image/arclogo")
def arclogo():
    return send_file("static/images/ARCLogo.png")

@images_bp.route("/image/arctablebackground")
def arcbkgrtable():
    return send_file("static/images/ARCTableBackground.png")

@images_bp.route("/image/cblogo")
def cblogo():
    return send_file("static/images/CBLogo.png")

@images_bp.route("/image/cbtablebackground")
def cbbkgrtable():
    return send_file("static/images/CBTableBackground.png")