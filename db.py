import os
from pathlib import Path

import pymysql

HERE = Path(__file__).resolve().parent


def _read_env_file(path):
    """Read a .env file in any common Windows encoding (UTF-8, UTF-8 with BOM,
    UTF-16 as written by PowerShell's `>`), and return a dict."""
    raw = path.read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        text = raw.decode("utf-16")
    else:
        text = raw.decode("utf-8-sig", errors="replace")
    values = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        values[key.strip()] = val
    return values


def load_env():
    """Load website/.env (or the .env one folder up). Returns the file used."""
    for path in (HERE / ".env", HERE.parent / ".env"):
        if path.is_file():
            for k, v in _read_env_file(path).items():
                os.environ[k] = v
            return path
    return None


ENV_FILE = load_env()


def get_conn(use_database=True):
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
         password="eidoo16",
        database=os.getenv("DB_NAME", "libraryDB") if use_database else None,
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


if __name__ == "__main__":
    # Connection checker:  python db.py
    print("Folder of db.py :", HERE)
    print(".env file used  :", ENV_FILE or "NOT FOUND  (create website/.env from .env.example)")
    print("DB_HOST         :", os.getenv("DB_HOST", "localhost"))
    print("DB_USER         :", os.getenv("DB_USER", "root"))
    pw = os.getenv("DB_PASSWORD", "")
    print("DB_PASSWORD     :", f"set ({len(pw)} characters)" if pw else "EMPTY")
    print("DB_NAME         :", os.getenv("DB_NAME", "libraryDB"))
    print()
    try:
        c = get_conn(use_database=False)
        print("[OK] MySQL login works.")
        c.close()
    except Exception as e:
        print("[FAIL] MySQL login:", e)
        if ENV_FILE is None:
            print("  -> No .env file was found next to db.py.")
        elif not pw:
            print("  -> .env was found but DB_PASSWORD is empty.")
        else:
            print("  -> The password in .env is not the MySQL root password.")
        raise SystemExit(1)
    try:
        c = get_conn()
        with c.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM Author")
            a = cur.fetchone()["n"]
            cur.execute("SELECT COUNT(*) AS n FROM Book")
            b = cur.fetchone()["n"]
        print(f"[OK] Database '{os.getenv('DB_NAME', 'libraryDB')}' found: {a} authors, {b} books.")
        c.close()
    except Exception as e:
        print("[FAIL] Database / tables:", e)
        print("  -> Run problem2_DDL.sql then problem2_DML.sql first.")
        raise SystemExit(1)