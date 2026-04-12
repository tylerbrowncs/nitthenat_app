import pyodbc
from datetime import datetime

# Allowed log types
ALLOWED_LOG_TYPES = {"INFO", "WARNING", "ERROR", "DEBUG","ACCESS","TEST", "MAKE_TABLE", "URL_SHORT"}

from utilities.sqldb_connection import SERVER, DATABASE, USERNAME, PASSWORD

# ---- CONNECTION STRING ----
conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    #"DRIVER={SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"UID={USERNAME};"
    f"PWD={PASSWORD};"
    "TrustServerCertificate=yes;"
)

def log(log_type: str, message: str, user: str):
    """
    Inserts a log into the database after validating the log type.
    
    :param log_type: Type of log (must be in ALLOWED_LOG_TYPES)
    :param log_datetime: datetime object
    :param message: log message (string)
    """
    log_datetime = datetime.now()

    # Validate log type
    if log_type not in ALLOWED_LOG_TYPES:
        raise ValueError(f"Invalid log type: {log_type}. Must be one of {ALLOWED_LOG_TYPES}")

    try:
        # Connect to database
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()


        # Insert log
        cursor.execute(
            """
            INSERT INTO nitthenat_logs (datetime, type, message, user_ip)
            VALUES (?, ?, ?, ?)
            """,
            log_datetime, log_type, message, user
        )

        conn.commit()

    except Exception as e:
        print(f"Failed to insert log: {e}")

    finally:
        cursor.close()
        conn.close()
        print("LOGGED")