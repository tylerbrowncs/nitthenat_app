import pyodbc, pytz
from datetime import datetime
from db_queries.db import get_cursor, get_db


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


    conn = get_db()
    cursor = get_cursor()


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

    return inserted_id

def get_image_bytes(table_id):
    conn = get_db()
    cursor = get_cursor()


    query = """
    SELECT table_image
    FROM dbo.nitthenat_tables
    WHERE table_id = ?
    """

    cursor.execute(query, (table_id,))
    row = cursor.fetchone()


    if row is None:
        return None

    return row[0]


def get_tables_by_user(user_id, page=1, per_page=10):

    cursor = get_cursor()

    offset = (page - 1) * per_page
    count_query = """
    SELECT COUNT(*)
    FROM dbo.nitthenat_tables
    WHERE created_by = ?;
    """

    cursor.execute(count_query, (user_id,))
    total_tables = cursor.fetchone()[0]

    query = """
    SELECT table_id, created_on, table_title
    FROM dbo.nitthenat_tables
    WHERE created_by = ?
    ORDER BY created_on DESC
    OFFSET ? ROWS
    FETCH NEXT ? ROWS ONLY;
    """

    cursor.execute(query, (user_id, offset, per_page))
    rows = cursor.fetchall()

    tables = [
        {
            "table_name": row.table_title,
            "table_id": row.table_id,
            "date_created": row.created_on
        }
        for row in rows
    ]

    return tables, total_tables


def delete_table(table_id):
    conn = get_db()
    cursor = get_cursor()

    query = """
    DELETE FROM dbo.nitthenat_tables
    WHERE table_id = ?;
    """

    cursor.execute(query, (table_id,))

    conn.commit()