import threading
import bcrypt, io
from PIL import Image

from flask import (
    Blueprint, copy_current_request_context,
    render_template, request, session,
    redirect, url_for, Response
)

from db_queries.accounts import (
    change_display_name, change_pass,
    create_user, get_user_by_username, upload_pfp
)
from db_queries.logger import log
from utils.limiter import limiter

accountsmgmt_bp = Blueprint("accounts_mgmt", __name__)


@accountsmgmt_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute; 50 per hour")
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == "GET":
        return render_template("login.html")

    username = (request.form.get('username') or "").lower()
    password = request.form.get('password') or ""

    try:
        user = get_user_by_username(username)
    except Exception as e:
        print(e)
        return render_template("403.html")

    if user:
        stored_hash = user["hashed_password"] 

        try:
            if bcrypt.checkpw(
                password.encode('utf-8'),
                stored_hash.encode('utf-8') 
            ):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['display_name'] = user["display_name"]

                ip = request.headers.get("X-Forwarded-For", request.remote_addr)
                if ip:
                    ip = ip.split(",")[0].strip()

                @copy_current_request_context
                def log_async():
                    log("LOGIN", session['username'], ip)

                threading.Thread(target=log_async, daemon=True).start()

                return redirect(url_for('home'))

        except ValueError:
            return render_template("login.html", error="Account error. Reset password.")

    return render_template("login.html", error="Invalid username or password!")


@accountsmgmt_bp.route("/register", methods=["GET", "POST"])
def register():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == "GET":
        return render_template("register.html")

    username = (request.form.get('username') or "").lower()
    password = request.form.get('password') or ""
    conf_password = request.form.get('conf-password') or ""

    if password != conf_password:
        return render_template("register.html", error="Passwords do not match!")

    if len(password) < 8:
        return render_template("register.html", error="Password must exceed 8 characters.")

    if get_user_by_username(username):
        return render_template("register.html", error="That username is already taken.")

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        create_user(username, hashed)

        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        if ip:
            ip = ip.split(",")[0].strip()

        @copy_current_request_context
        def log_async():
            log("REGISTER", username, ip)

        threading.Thread(target=log_async, daemon=True).start()

        return redirect(url_for('accounts_mgmt.login'))

    except Exception as e:
        print(e)
        return render_template("403.html")


# ================= LOGOUT =================
@accountsmgmt_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))


# ================= PROFILE =================
@accountsmgmt_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    if request.method == "POST":
        form_type = request.form.get('form_type')

        if form_type == "profile_pic":
            file = request.files.get('profile_pic')

            if not file or file.filename == '':
                return render_template("profile.html", error="Upload an image.")

            try:
                img = Image.open(file)
                img = img.convert("RGBA")

                buffer = io.BytesIO()
                img.save(buffer, format="PNG")

                upload_pfp(session["user_id"], buffer.getvalue())

                return render_template("profile.html", info="Profile picture changed.")
            except Exception as e:
                print(e)
                return render_template("profile.html", error="Invalid file type.")

        if form_type == "display_name":
            name = request.form.get('display_name')

            try:
                change_display_name(session["user_id"], name)
                session["display_name"] = name
                return render_template("profile.html", info="Display name changed!")
            except Exception as e:
                print(e)
                return render_template("profile.html", error="Unable to change display name.")
            
        if form_type == "password":
            current_password = request.form.get('current_password') or ""
            new_password = request.form.get('new_password') or ""
            confirm_password = request.form.get('confirm_password') or ""

            if new_password != confirm_password:
                return render_template("profile.html", error="Passwords do not match!")

            if len(new_password) < 8:
                return render_template("profile.html", error="Password must exceed 8 characters.")

            user = get_user_by_username(session["username"])

            if not user:
                return render_template("403.html")

            stored_hash = user["hashed_password"]

            try:
                if bcrypt.checkpw(
                    current_password.encode('utf-8'),
                    stored_hash.encode('utf-8')
                ):
                    
            
                    new_hash = bcrypt.hashpw(
                        new_password.encode('utf-8'),
                        bcrypt.gensalt()
                    ).decode('utf-8')

                    change_pass(session["user_id"], new_hash)

                    return render_template("profile.html", info="Password Changed!")
                else:
                    return render_template("profile.html", error="Incorrect current password.")

            except ValueError:
                return render_template("profile.html", error="Password system error.")

    return render_template("profile.html", info=None, error=None)

@accountsmgmt_bp.route('/profile/image/<username>')
def profile_image(username):
    user = get_user_by_username(username)

    if not user or not user["profile_pic_bin"]:
        return redirect(url_for('static', filename='images/default_pfp.png'))

    return Response(user["profile_pic_bin"], mimetype='image/png')