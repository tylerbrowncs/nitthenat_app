from io import BytesIO

from flask import Blueprint, render_template, send_file

import json,os

from db_queries.tables import get_image_bytes

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/tournements")
def tourneys():
    return render_template("tournements.html")


@pages_bp.route("/zak")
def zak():
    return render_template("zak.html")


@pages_bp.route("/timetrials")
def timetrials():
    tracks = load_static_data()["tracks"]
    return render_template("timetrials.html", tracks=tracks)


def load_static_data(file_path="static_data.json"):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_path}")
        return {}