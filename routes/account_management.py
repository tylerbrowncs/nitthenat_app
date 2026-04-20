import threading

from flask import Blueprint, copy_current_request_context, render_template, request, send_file, session, redirect, url_for

import bcrypt

from db_queries.accounts import create_user, get_user_by_username
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

    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            user = get_user_by_username(username)

        except:
            return render_template("403.html")

        if user:
            stored_hash = user["hashed_password"]

            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')

            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                session['user_id'] = user['id']
                session['username'] = user['username']
                try:
                    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

                    if ip:
                        ip = ip.split(",")[0].strip()

                except:
                    ip = request.remote_addr
                @copy_current_request_context
                def log_async():
                    log("LOGIN", session['username'], ip)

                threading.Thread(
                    target=log_async,
                    daemon=True
                ).start()
                return redirect(url_for('home'))


        return render_template("login.html", error="Invalid username or password!")

@accountsmgmt_bp.route("/register", methods=["GET", "POST"])
def register():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == "GET":
        return render_template("register.html")
    
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        conf_password = request.form.get('conf-password')

        if password != conf_password:
            return render_template("register.html", error="Passwords do not match!")
        
        if len(password) < 8:
            return render_template("register.html", error="Password must exceed 8 characters.")
        

        if get_user_by_username(username) is not None:
            return render_template("register.html", error="That username is already taken.")

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed = hashed.decode("utf-8")

        try:
            create_user(username, hashed)
            try:
                ip = request.headers.get("X-Forwarded-For", request.remote_addr)

                if ip:
                    ip = ip.split(",")[0].strip()

            except:
                ip = request.remote_addr

            
            @copy_current_request_context
            def log_async():
                log("REGISTER", username, ip)

            threading.Thread(
                target=log_async,
                daemon=True
            ).start()

            return redirect(url_for('accounts_mgmt.login'))
        
        except Exception as e:
            raise e
            return render_template("403.html")



@accountsmgmt_bp.route("/logout")
def logout():
    session.clear()
    return (redirect(url_for('home')))