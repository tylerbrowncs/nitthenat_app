from flask import Blueprint, request, current_app, render_template, redirect, send_file

from datetime import datetime
import threading, os

from utils.logger import log
from utils.countires import COUNTRY_CODES, COUNTRY_NAMES
from utils.coloring import hex_to_rgb
from utils.generator_urls import generate_string
from utils.table_generator import generate_war_image

tables_bp = Blueprint("tables", __name__)


@tables_bp.route('/mk-tablemaker/6v6', methods=["GET", "POST"])
def mktable6v6():
    try:
        file_path_table = None
        filename = None

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

            base_dir = current_app.root_path

            filename = datetime.now().strftime("%d%m") + generate_string(
                len(os.listdir(os.path.join(base_dir, "static", "images", "tables")))
            ) + datetime.now().strftime("%y")+ ".png"

            file_path_table = os.path.join(
                base_dir,
                "static",
                "images",
                "tables",
                filename
            )

            color = hex_to_rgb(request.form.get("favcolor"))

            generate_war_image(data, file_path_table, bg_url, title, subtitle, color)

            #TRACK TABLE CREATION

            try:
                ip = request.headers.get("X-Forwarded-For", request.remote_addr)

                if ip:
                    ip = ip.split(",")[0].strip()

            except:
                ip = request.remote_addr

            threading.Thread(
                target=log,
                args=("MAKE_TABLE", f"{filename}", ip),
                daemon=True
            ).start()
            return redirect("/table/" + filename)
    except:
        return render_template("404.html"), 404

    return render_template("mktablemaker-6v6.html", COUNTRY_NAMES=COUNTRY_NAMES, filename=None)

@tables_bp.route("/table/<image>")
def table(image):
    if os.path.exists("static/images/tables/"+image):
        return send_file("static/images/tables/"+image)
    else:
        return render_template("404_url_shortener.html")
    
    

