import pyodbc
from flask import g

from sqldb_connection import SERVER, DATABASE, USERNAME, PASSWORD, DRIVER

conn_str = (
    f"DRIVER={DRIVER};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"UID={USERNAME};"
    f"PWD={PASSWORD};"
    "TrustServerCertificate=yes;"
)

def get_db():
    if 'db' not in g:
        g.db = pyodbc.connect(conn_str)
    return g.db


def get_cursor():
    return get_db().cursor()


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()