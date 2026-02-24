from flask import Flask, current_app,redirect, request, render_template_string, render_template, send_file

from utilities.generator_urls import generate_string
from utilities.table_generator import generate_war_image
from utilities.countires import COUNTRY_CODES, COUNTRY_NAMES
from datetime import datetime
import json, os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/mkw100")
def mkw100():
    return render_template("100percentMKW.html")



@app.route("/image/offline")
def imgoff():
    return send_file("static/images/offline.png")


@app.route("/image/profile")
def imgprof():
    return send_file("static/images/profile.png")

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

    return render_template("shorten.html", short_url=short_url)

@app.route('/r/<code>')
def reverse_proxy(code):
    urls = load_urls()

    if code in urls:
        return redirect(urls[code])
    else:
        return render_template("404.html"), 404
    

#######################################
#
#   Table Generator
#
#######################################

@app.route('/mk-tablemaker/6v6', methods=["GET", "POST"])
def mktable6v6():
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

        filename = generate_string(
            len(os.listdir(os.path.join(base_dir, "static", "images", "tables")))
        ) + ".png"

        file_path_table = os.path.join(
            base_dir,
            "static",
            "images",
            "tables",
            filename
        )

        generate_war_image(data, file_path_table, bg_url, title, subtitle)
        return redirect("/table/" + filename)

    return render_template("mktablemaker-6v6.html", COUNTRY_NAMES=COUNTRY_NAMES, filename=None)

@app.route("/table/<image>")
def table(image):
    return send_file("static/images/tables/"+image)


#######################################
#######################################
#######################################


if __name__ == "__main__":
    app.run(debug=True)

