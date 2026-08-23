from db_queries.db import get_cursor, get_db

def create_user(username, hashed_password):
    cursor = get_cursor()
    cursor.execute("""
        INSERT INTO nitthenat_users (username, hashed_password, email, role, display_name)
        VALUES (%s, %s, NULL, 'user', %s)
    """, (username, hashed_password, username))
    get_db().commit()


def get_user_by_username(username):
    # Use dictionary=True to preserve dict-style/named access for rows
    cursor = get_db().cursor(dictionary=True)
    cursor.execute("""
        SELECT id, username, hashed_password, role, display_name, profile_pic
        FROM nitthenat_users
        WHERE username = %s
    """, (username,))

    user = cursor.fetchone()
    if user:
        return {
            "id": user["id"],
            "username": user["username"],
            "hashed_password": user["hashed_password"],
            "role": user["role"],
            "display_name": user["display_name"],
            "profile_pic_bin": user["profile_pic"]
        }
    
    return None


def upload_pfp(user_id, pic_bin):
    cursor = get_cursor()
    cursor.execute("""
        UPDATE nitthenat_users
        SET profile_pic = %s
        WHERE id = %s
    """, (pic_bin, user_id))
    get_db().commit()


def delete_pfp(user_id):
    cursor = get_cursor()
    cursor.execute("""
        UPDATE nitthenat_users
        SET profile_pic = %s
        WHERE id = %s
    """, (None, user_id))
    get_db().commit()


def change_display_name(user_id, name):
    cursor = get_cursor()
    cursor.execute("""
        UPDATE nitthenat_users
        SET display_name = %s
        WHERE id = %s
    """, (name, user_id))
    get_db().commit()


def change_pass(user_id, new_hash):
    cursor = get_cursor()
    cursor.execute("""
        UPDATE nitthenat_users
        SET hashed_password = %s
        WHERE id = %s
    """, (new_hash, user_id))
    get_db().commit()