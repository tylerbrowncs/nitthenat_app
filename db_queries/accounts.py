import pyodbc, pytz

from sqldb_connection import SERVER, DATABASE, USERNAME, PASSWORD, DRIVER
from db_queries.db import get_cursor, get_db
# ---- CONNECTION STRING ----
conn_str = (
    f"DRIVER={DRIVER};"
    #"DRIVER={SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"UID={USERNAME};"
    f"PWD={PASSWORD};"
    "TrustServerCertificate=yes;"
)

def create_user(username, hashed_password):
    cursor = get_cursor()
    cursor.execute("""
        INSERT INTO nitthenat_users (username, hashed_password, email, role)
        VALUES (?, ?, NULL, 'user')
    """, (username, hashed_password))
    get_db().commit()



def get_user_by_username(username):
    cursor = get_cursor()
    cursor.execute("""
        SELECT id, username, hashed_password, role
        FROM nitthenat_users
        WHERE username = ?
    """, (username,))

    user = cursor.fetchone()
    if user:
        return {
            "id": user.id,
            "username": user.username,
            "hashed_password": user.hashed_password,
            "role": user.role
        }
    
    return None