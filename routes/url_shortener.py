from flask import Blueprint, render_template, request, redirect

from utils.generator_urls import generate_string
from db_queries.logger import log

import threading, requests, json, os

shortener_bp = Blueprint("shortener", __name__)


URL_FILE = "urls.json"

def load_urls():
    if not os.path.exists(URL_FILE):
        return {}
    with open(URL_FILE, "r") as f:
        return json.load(f)

def save_urls(data):
    with open(URL_FILE, "w") as f:
        json.dump(data, f, indent=4)

@shortener_bp.route("/shorten", methods=["GET", "POST"])
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

@shortener_bp.route('/r/<code>')
def reverse_proxy(code):
    urls = load_urls()

    if code in urls:
        return redirect(urls[code])
    else:
        return render_template("404_url_shortener.html"), 404