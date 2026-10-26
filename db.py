import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password="eidoo16",
        database=os.getenv("DB_NAME", "library"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )

def query(sql, args=(), one=False):
    """SELECT: returns a list of dicts (or one dict / None when one=True)."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            rows = cur.fetchall()
        if one:
            return rows[0] if rows else None
        return rows
    except Exception as e:
        print("\n========== DATABASE ERROR IN QUERY ==========")
        print(f"QUERY: {sql}")
        print(f"ERROR: {e}")
        print("=============================================\n")
        raise e
    finally:
        conn.close()

def execute(sql, args=()):
    """INSERT / UPDATE / DELETE: returns the number of affected rows."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            return cur.execute(sql, args)
    except Exception as e:
        print("\n========== DATABASE ERROR IN EXECUTE ==========")
        print(f"QUERY: {sql}")
        print(f"ERROR: {e}")
        print("===============================================\n")
        raise e
    finally:
        conn.close()
