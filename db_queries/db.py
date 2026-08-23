import mysql.connector
from flask import g

from sqldb_connection import SERVER, DATABASE, USERNAME, PASSWORD, PORT

DB_CONFIG = {
    "host": SERVER,
    "user": USERNAME,
    "password": PASSWORD,
    "database": DATABASE,
    "port": PORT if "PORT" in locals() else 3306,
    "autocommit": True,
}


def get_db():
    if "db" not in g:
        g.db = mysql.connector.connect(**DB_CONFIG)
    return g.db


def get_cursor():
    return get_db().cursor(buffered=True)


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None and db.is_connected():
        db.close()