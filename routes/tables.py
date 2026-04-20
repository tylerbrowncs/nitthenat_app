from io import BytesIO

from flask import Blueprint, request, current_app, render_template, redirect, send_file, session, copy_current_request_context

from datetime import datetime
import threading, os

from db_queries.logger import log
from db_queries.tables import get_image_bytes, get_tables_by_user, save_image
from utils.countires import COUNTRY_CODES, COUNTRY_NAMES
from utils.coloring import hex_to_rgb
from utils.generator_urls import generate_string
from utils.table_generator import generate_war_image

tables_bp = Blueprint("tables", __name__)


@tables_bp.route('/mk-tablemaker/6v6', methods=["GET", "POST"])
def mktable6v6():
    try:

        if request.method == "POST":


            bg_url = request.form.get(f"background_url")

            if bg_url == "" or bg_url == None:
                bg_url = "https://nitthenat.com/image/offline"
            
            title = request.form.get(f"title_text")
            if title == "":
                title = "WAR RESULTS"
            team1 = {}

            subtitle = request.form.get(f"subtitle")

            if subtitle == "":
                subtitle = datetime.now().strftime("%b %d, %Y")

            team1["name"] = request.form.get(f"team1_name")
            team1["icon"] = request.form.get(f"team1_icon")

            team1["members"] = [
                {"name": request.form.get(f"team1_p{i}_name"), 
                "country": COUNTRY_CODES[COUNTRY_NAMES.index(request.form.get(f"team1_p{i}_country"))],
                "score": int(request.form.get(f"team1_p{i}_score"))
                } 
                
                for i in range(6)]
            

            team2 = {}

            team2["name"] = request.form.get(f"team2_name")
            team2["icon"] = request.form.get(f"team2_icon")

            team2["members"] = [
                {"name": request.form.get(f"team2_p{i}_name"), 
                "country": COUNTRY_CODES[COUNTRY_NAMES.index(request.form.get(f"team2_p{i}_country"))],
                "score": int(request.form.get(f"team2_p{i}_score"))
                } 
                
                for i in range(6)]
            
            data = {
                "teams":[team1, team2]
            }

            color = hex_to_rgb(request.form.get("favcolor"))

            new_table = generate_war_image(data, bg_url, title, subtitle, color)

            if "user_id" in session:
                user = session["user_id"]
            else:
                user = None

            try:

                table_id = save_image(new_table, user, title)

            except:
                return render_template("403.html")

            #TRACK TABLE CREATION

            try:
                ip = request.headers.get("X-Forwarded-For", request.remote_addr)

                if ip:
                    ip = ip.split(",")[0].strip()

            except:
                ip = request.remote_addr

            @copy_current_request_context
            def log_async():
                log("MAKE_TABLE", f"{table_id}", ip)

            threading.Thread(
                target=log_async,
                daemon=True
            ).start()
            return redirect("/table/" + table_id)
    except Exception as e:
        return render_template("404.html"), 404

    return render_template("mktablemaker-6v6.html", COUNTRY_NAMES=COUNTRY_NAMES, filename=None)

@tables_bp.route("/table/<image>")
def table(image):

    try:

        image_bytes = get_image_bytes(image)


    except:
        return render_template("403.html")

    if not image_bytes:
        return render_template("404.html")

    return send_file(
        BytesIO(image_bytes),   # ← convert bytes → file-like object
        mimetype="image/png"    # ← IMPORTANT: match your stored format

    )


@tables_bp.route("/tables")
def tables():
    if "user_id" not in session:
        return redirect("tables.mktable6v6")
    

    user_tables = get_tables_by_user(session["user_id"])
    tables = [
        {"table_name": "Nat vs12314 Tyler",
         "table_id": "hjdsf04",
        "date_created": "10/10/10 10:10"},
        {"table_name": "Nat vs453 Tyler",
         "table_id": "hjdsf04",
        "date_created": "10/10/10 10:10"},
        {"table_name": "Nat vs123123 Tyler",
         "table_id": "hjdsf04",
        "date_created": "10/10/10 10:10"},
        {"table_name": "Nat vs123Tyler",
         "table_id": "hjdsf04",
        "date_created": "10/10/10 10:10"},
        {"table_name": "Nat vs 123Tyler",
         "table_id": "hjdsf04",
        "date_created": "10/10/10 10:10"},

    ]
    return render_template("my_tables.html", tables=user_tables)
    

