import pytz
from datetime import datetime

from db_queries.db import get_db, get_cursor  

# Allowed log types
ALLOWED_LOG_TYPES = {"INFO", "WARNING", "ERROR", "DEBUG", "ACCESS", "TEST", "MAKE_TABLE", "URL_SHORT", "LOGIN", "REGISTER"}

dev_skip_logging = False


def log(log_type: str, message: str, user: str):
    """
    Inserts a log into the database after validating the log type.
    """

    if dev_skip_logging:
        return
    
    if log_type not in ALLOWED_LOG_TYPES:
        raise ValueError(f"Invalid log type: {log_type}. Must be one of {ALLOWED_LOG_TYPES}")

    lon = pytz.timezone('Europe/London')
    log_datetime = datetime.now(lon)

    try:
        conn = get_db()     
        cursor = get_cursor() 

        cursor.execute(
            """
            INSERT INTO nitthenat_logs (datetime, type, message, user_ip)
            VALUES (?, ?, ?, ?)
            """,
            log_datetime, log_type, message, user
        )

        conn.commit()

    except Exception as e:
        print(f"Failed to insert log: {e}", flush=True)
        print("LOGGED", flush=True)

    finally:
        try:
            cursor.close()
        except:
            pass

        print("LOGGED")