from flask import Flask, current_app,redirect, request, render_template_string, render_template, send_file
from utilities.coloring import hex_to_rgb
from utilities.generator_urls import generate_string
from utilities.table_generator import generate_war_image
from utilities.countires import COUNTRY_CODES, COUNTRY_NAMES
from utilities.liveChecker import isLive
from utilities.logger import log
from datetime import datetime
import json, os, threading

app = Flask(__name__)

STAT_FILE = "stats.json"

@app.route("/")
def home():
    live = isLive('nitthenat')
    return render_template("home.html", live=live)

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.route("/image/offline")
def imgoff():
    return send_file("static/images/offline.png")


@app.route("/image/profile")
def imgprof():
    return send_file("static/images/profile.png")

@app.route("/tournements")
def tourneys():
    return render_template("tournements.html")

#######################################
#
#   Tracking
#
########################################
def isValidRoute(route):
    for rule in app.url_map.iter_rules():
        if rule.rule == route:
            return True
        
    return False

@app.after_request
def track_page_views(response):

    if request.path.startswith(("/r","/image", "/static", "/favicon.ico", "/table")):
        return response
    
    if not isValidRoute(request.path):
        return response
    
    if os.path.exists(STAT_FILE):
        try:
            with open(STAT_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}


    if request.path not in data:
        data[request.path] = {
            "total_views": 0
        }


    data[request.path]["total_views"] += 1

    with open(STAT_FILE, "w") as f:
        json.dump(data, f, indent=4)

    try:
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)

        if ip:
            ip = ip.split(",")[0].strip()

    except:
        ip = request.remote_addr

    path = request.path

    
    threading.Thread(
        target=log,
        args=("ACCESS", f"{path}", ip),
        daemon=True
    ).start()


    return response

#######################################
#
#   POSTS
#
########################################

@app.route("/mkw100")
def mkw100():
    return render_template("posts/post_MKW100p.html")

#######################################
#
#   URL SHORTENER
#
########################################

URL_FILE = "urls.json"

def load_urls():
    if not os.path.exists(URL_FILE):
        return {}
    with open(URL_FILE, "r") as f:
        return json.load(f)

def save_urls(data):
    with open(URL_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/shorten", methods=["GET", "POST"])
def shorten():
    short_url = None

    if request.method == "POST":
        original_url = request.form.get("url")

        if original_url:
            urls = load_urls()

            code = generate_string(len(urls))

            # Prevent duplicate code collision
            while code in urls:
                code = generate_string(len(urls))

            urls[code] = original_url
            save_urls(urls)

            short_url = "https://nitthenat.com/r/" + code

            try:
                ip = request.headers.get("X-Forwarded-For", request.remote_addr)

                if ip:
                    ip = ip.split(",")[0].strip()

            except:
                ip = request.remote_addr

            threading.Thread(
                target=log,
                args=("URL_SHORT", f"{original_url} > {short_url}", ip),
                daemon=True
            ).start()

    return render_template("shorten.html", short_url=short_url)

@app.route('/r/<code>')
def reverse_proxy(code):
    urls = load_urls()

    if code in urls:
        return redirect(urls[code])
    else:
        return render_template("404_url_shortener.html"), 404
    

#######################################
#
#   Table Generator
#
#######################################

@app.route('/mk-tablemaker/6v6', methods=["GET", "POST"])
def mktable6v6():
    try:
        app.logger.info(len(os.listdir("static/images/tables")))
        file_path_table = None
        filename = None

        if request.method == "POST":
            app.logger.info(len(os.listdir("static/images/tables")))


            bg_url = request.form.get(f"background_url")

            if bg_url == "" or bg_url == None:
                bg_url = "https://nitthenat.com/image/offline"
            
            title = request.form.get(f"title_text")
            if title == "":
                title = "WAR RESULTS"
            app.logger.info(title)
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
            app.logger.info(data)

            generate_war_image(data, file_path_table, bg_url, title, subtitle, color)

            #TRACK TABLE CREATION
    
            if os.path.exists(STAT_FILE):
                try:
                    with open(STAT_FILE, "r") as f:
                        data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
            else:
                data = {}


            if "tables_created" not in data:
                data["tables_created"] = {
                    "6v6": 0
                }


            data["tables_created"]["6v6"] += 1

            with open(STAT_FILE, "w") as f:
                json.dump(data, f, indent=4)

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

@app.route("/table/<image>")
def table(image):
    if os.path.exists("static/images/tables/"+image):
        return send_file("static/images/tables/"+image)
    else:
        return render_template("404_url_shortener.html")


@app.route("/zak")
def zak():
    return render_template("zak.html")


@app.route("/timetrials")
def timetrials():

    tracks = load_static_data()["tracks"]
    return render_template("timetrials.html", tracks=tracks)

#######################################
#######################################
#######################################

import json

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


if __name__ == "__main__":
    app.run(debug=True)

