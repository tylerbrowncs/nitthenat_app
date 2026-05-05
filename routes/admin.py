import bcrypt
from flask import Blueprint, render_template, session, request, current_app

from db_queries.accounts import change_pass, delete_pfp, get_user_by_username
from db_queries.tables import delete_table, get_tables_by_user

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin", methods=["GET", "POST"])
def admin():
    user = get_user_by_username(session['username'])
    session['role'] = user['role']

    if session["role"] != "admin":
        return render_template("404.html")
    
    user = None
    username = None
    tables = None
    message = None
    error = None
    

    if request.method == "POST":
        form_type = request.form.get('form_type')
        username = request.form.get('username')

        if request.form.get('username') == "":
            return render_template("admin.html", error="Please enter a valid username")
        
        user = get_user_by_username(username)

  

        if user == None:
            return render_template("admin.html", error="A user with than name doesn't exist.")

        if form_type == "change_password":
            new_password = request.form.get("new_password")
            user_id = request.form.get("user_id")

            new_hash = bcrypt.hashpw(
                        new_password.encode('utf-8'),
                        bcrypt.gensalt()
                    ).decode('utf-8')

            change_pass(user_id, new_hash)
            message = "Password has been changed."

        if form_type == "reset_pfp":
            user_id = request.form.get("user_id")

            delete_pfp(user_id)
            message = "Profile picture removed."

        if form_type == "delete_table":
            table_id = request.form.get("tableID")
            try:
                delete_table(table_id)
                message = f"Successfully delete {username}'s table: {table_id}"
            except:
                error = "Could not delete table, try again later."
            

        tables = get_tables_by_user(user["id"])
        formatted_tables = []
        for table in tables:
            table["date_created"] = format_date(table["date_created"])
            formatted_tables += [table]

        return render_template("admin.html", user=user, tables=formatted_tables, username=username, message=message, error=error)

    return render_template("admin.html", username=username, message=message)

from datetime import datetime

def format_date(dt):
    suffix = lambda d: "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")

    return dt.strftime(f"%a {dt.day}{suffix(dt.day)} %B, %H:%M:%S")