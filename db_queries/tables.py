import pyodbc, pytz
from datetime import datetime


from sqldb_connection import SERVER, DATABASE, USERNAME, PASSWORD, DRIVER

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

def save_image(img_bytes, user=None, table_title=None):


    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    query = """
    INSERT INTO nitthenat_tables (table_image, created_by, created_on, table_title)
    OUTPUT INSERTED.table_id
    VALUES (?, ?, ?, ?)
    """
    lon = pytz.timezone('Europe/London')
    created_on = datetime.now(lon)

    cursor.execute(query, (img_bytes, user, created_on, table_title))

    inserted_id = cursor.fetchone()[0]

    conn.commit()
    cursor.close()
    conn.close()

    return inserted_id

def get_image_bytes(table_id):
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    query = """
    SELECT table_image
    FROM dbo.nitthenat_tables
    WHERE table_id = ?
    """

    cursor.execute(query, (table_id,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row is None:
        return None

    return row[0]


def get_tables_by_user(user_id):
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    query = """
    SELECT table_id, created_on, table_title
    FROM dbo.nitthenat_tables
    WHERE created_by = ?
    ORDER BY created_on DESC
    """

    cursor.execute(query, (user_id,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {"table_name": row.table_title,
         "table_id": row.table_id,
         "date_created": row.created_on}
         for row in rows
    ]