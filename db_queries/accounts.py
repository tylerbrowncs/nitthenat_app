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
        INSERT INTO nitthenat_users (username, hashed_password, email, role, display_name)
        VALUES (?, ?, NULL, 'user', ?)
    """, (username, hashed_password, username))
    get_db().commit()



def get_user_by_username(username):
    cursor = get_cursor()
    cursor.execute("""
        SELECT id, username, hashed_password, role, display_name, profile_pic
        FROM nitthenat_users
        WHERE username = ?
    """, (username,))

    user = cursor.fetchone()
    if user:
        return {
            "id": user.id,
            "username": user.username,
            "hashed_password": user.hashed_password,
            "role": user.role,
            "display_name": user.display_name,
            "profile_pic_bin": user.profile_pic
        }
    
    return None


def upload_pfp(user_id, pic_bin):
    cursor = get_cursor()
    
    cursor.execute("""
        UPDATE nitthenat_users
        SET profile_pic = ?
        WHERE id = ?
    """, (pic_bin, user_id))
    
    cursor.connection.commit()


def change_display_name(user_id, name):
    cursor = get_cursor()
    
    cursor.execute("""
        UPDATE nitthenat_users
        SET display_name = ?
        WHERE id = ?
    """, (name, user_id))
    
    cursor.connection.commit()


def change_pass(user_id, new_hash):
    cursor = get_cursor()
    
    cursor.execute("""
        UPDATE nitthenat_users
        SET hashed_password = ?
        WHERE id = ?
    """, (new_hash, user_id))
    
    cursor.connection.commit()