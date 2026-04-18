from flask import Blueprint, render_template

posts_bp = Blueprint("posts", __name__)

@posts_bp.route("/mkw100")
def mkw100():
    return render_template("posts/post_MKW100p.html")