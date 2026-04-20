from flask import Flask, current_app,redirect, request, render_template_string, render_template, send_file, copy_current_request_context
from utils.coloring import hex_to_rgb
from utils.generator_urls import generate_string
from utils.table_generator import generate_war_image
from utils.countires import COUNTRY_CODES, COUNTRY_NAMES
from utils.liveChecker import isLive
from db_queries.logger import log
from datetime import datetime
from config import SECRET
from utils.limiter import limiter


import json, os, threading




app = Flask(__name__)

limiter.init_app(app)

app.config.update(
    SECRET_KEY="SECRET",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,   # only if HTTPS
    SESSION_COOKIE_SAMESITE='Lax'
)
#######################################
#
#              Blueprints
#                                   
#######################################

from routes.pages import pages_bp
app.register_blueprint(pages_bp)

from routes.images import images_bp
app.register_blueprint(images_bp)

from routes.posts import posts_bp
app.register_blueprint(posts_bp)

from routes.url_shortener import shortener_bp
app.register_blueprint(shortener_bp)

from routes.tables import tables_bp
app.register_blueprint(tables_bp)

from routes.account_management import accountsmgmt_bp
app.register_blueprint(accountsmgmt_bp)

#######################################
#
#                Home
#                                   
#######################################

@app.route("/")
def home():
    live = isLive('nitthenat')
    return render_template("home.html", live=live)

#######################################
#
#                 404
#                                   
#######################################

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

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

    if request.path.startswith(("/r", "/image", "/static", "/favicon.ico")) \
    or request.path == "/table":
        return response
    if not isValidRoute(request.path):
        return response

    path = request.path

    try:
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        if ip:
            ip = ip.split(",")[0].strip()
    except:
        ip = request.remote_addr


    @copy_current_request_context
    def log_async():
        log("ACCESS", path, ip)

    threading.Thread(
        target=log_async,
        daemon=True
    ).start()

    return response


#######################################
#######################################
#######################################

if __name__ == "__main__":
    app.run(debug=True)

