import bcrypt
import math
from flask import Blueprint, render_template, session, request, current_app

from db_queries.accounts import change_pass, delete_pfp, get_user_by_username
from db_queries.tables import delete_table, get_tables_by_user

admin_bp = Blueprint("admin", __name__)

from flask import Blueprint, render_template, request, session, redirect, url_for
import bcrypt
import math, time

@admin_bp.route("/admin", methods=["GET", "POST"])
def admin():

    route_start = time.perf_counter()
    user = get_user_by_username(session["username"])
    session["role"] = user["role"]

    if session["role"] != "admin":
        return render_template("404.html")

    message = None
    error = None

    # Number of tables per page
    per_page = 10

    ############################################################
    # Handle POST actions
    ############################################################

    if request.method == "POST":

        form_type = request.form.get("form_type")
        username = request.form.get("username")
        page = request.form.get("page", 1, type=int)

        if not username:
            return redirect(url_for("admin.admin"))

        user = get_user_by_username(username)

        if user is None:
            return render_template(
                "admin.html",
                error="A user with that name doesn't exist."
            )

        ########################################################
        # Change Password
        ########################################################

        if form_type == "change_password":

            new_password = request.form.get("new_password")
            user_id = request.form.get("user_id")

            new_hash = bcrypt.hashpw(
                new_password.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            change_pass(user_id, new_hash)

            message = "Password has been changed."

        ########################################################
        # Reset Profile Picture
        ########################################################

        elif form_type == "reset_pfp":

            user_id = request.form.get("user_id")

            delete_pfp(user_id)

            message = "Profile picture removed."

        ########################################################
        # Delete Table
        ########################################################

        elif form_type == "delete_table":

            table_id = request.form.get("tableID")

            try:
                delete_table(table_id)
                message = f"Successfully deleted table {table_id}"
            except Exception:
                error = "Could not delete table."

        ########################################################
        # Reload data after action
        ########################################################

        tables, total_tables = get_tables_by_user(
            user["id"],
            page=page,
            per_page=per_page
        )

        formatted_tables = []

        for table in tables:
            table["date_created"] = format_date(table["date_created"])
            formatted_tables.append(table)

        total_pages = max(1, math.ceil(total_tables / per_page))

        return render_template(
            "admin.html",
            user=user,
            username=username,
            tables=formatted_tables,
            page=page,
            total_pages=total_pages,
            message=message,
            error=error
        )

    ############################################################
    # Page
    ############################################################

    username = request.args.get("username")
    page = request.args.get("page", 1, type=int)

    if not username:
        return render_template("admin.html")

    user = get_user_by_username(username)

    if user is None:
        return render_template(
            "admin.html",
            username=username,
            error="A user with that name doesn't exist."
        )

    tables, total_tables = get_tables_by_user(
        user["id"],
        page=page,
        per_page=per_page
    )

    formatted_tables = []

    for table in tables:
        table["date_created"] = format_date(table["date_created"])
        formatted_tables.append(table)

    total_pages = max(1, math.ceil(total_tables / per_page))

    print(f"Entire route took {time.perf_counter() - route_start:.3f}s")


    t = time.perf_counter()

    html = render_template(
        "admin.html",
        user=user,
        username=username,
        tables=formatted_tables,
        page=page,
        total_pages=total_pages,
    )

    print(f"Template render: {time.perf_counter()-t:.3f}s")

    return html
from datetime import datetime

def format_date(dt):
    suffix = lambda d: "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")

    return dt.strftime(f"%a {dt.day}{suffix(dt.day)} %B, %H:%M:%S")