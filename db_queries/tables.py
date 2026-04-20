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

def save_image(img_bytes, user=None):


    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    query = """
    INSERT INTO nitthenat_tables (table_image, created_by, created_on)
    OUTPUT INSERTED.table_id
    VALUES (?, ?, ?)
    """
    created_on = datetime.now()

    cursor.execute(query, (img_bytes, user, created_on))

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

    cursor.execute(query, (table_id,))  # ← FIXED
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row is None:
        return None

    return row[0]