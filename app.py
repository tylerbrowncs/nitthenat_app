from flask import Flask, redirect, request, render_template_string, render_template, send_file

from utilities.generator_urls import generate_string
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




if __name__ == "__main__":
    app.run(debug=True)



#
#
#   URL SHORTENER
#
#

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
