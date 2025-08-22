import os
import time
import logging
from flask import Flask, render_template, request, redirect, flash
import pymysql

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change_me")
app.debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"

# Env-driven DB config (works for both RDS and compose)
DB_HOST = os.getenv("DB_HOST", "db")              # default to compose service name
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASS = os.getenv("DB_PASS", "appsecret")
DB_NAME = os.getenv("DB_NAME", "mydb")

# Optional SSL (useful for RDS). Set DB_SSL_MODE=required and DB_SSL_CA=/path/to/rds-ca-*.pem
DB_SSL_MODE = os.getenv("DB_SSL_MODE", "disabled")      # disabled|required
DB_SSL_CA = os.getenv("DB_SSL_CA")                      # path to CA bundle if needed

CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "5"))
WAIT_STARTUP_SECS = int(os.getenv("DB_WAIT_STARTUP_SECS", "120"))

logging.basicConfig(level=logging.INFO)

def _ssl_args():
    if DB_SSL_MODE.lower() == "required":
        # If you have an RDS CA bundle, set DB_SSL_CA to its path in the container
        if DB_SSL_CA and os.path.exists(DB_SSL_CA):
            return {"ssl": {"ca": DB_SSL_CA}}
        # If CA not provided, still try SSL (server’s cert won’t be verified)
        return {"ssl": {}}
    return {}

def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        connect_timeout=CONNECT_TIMEOUT,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        **_ssl_args()
    )

def wait_for_db(max_seconds=WAIT_STARTUP_SECS):
    start = time.time()
    while True:
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            conn.close()
            logging.info("Database is reachable at %s:%s.", DB_HOST, DB_PORT)
            break
        except Exception as e:
            if time.time() - start > max_seconds:
                logging.exception("Database not ready within %ss", max_seconds)
                raise
            logging.warning("Waiting for DB %s:%s ... (%s)", DB_HOST, DB_PORT, e)
            time.sleep(2)

def ensure_schema():
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) NOT NULL,
                    phone VARCHAR(30),
                    place VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
        conn.close()
        logging.info("Ensured 'users' table exists.")
    except Exception as e:
        logging.exception("Failed to ensure schema: %s", e)
        raise

@app.before_first_request
def init_app():
    wait_for_db()
    ensure_schema()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        phone = request.form.get("phone", "").strip()
        place = request.form.get("place", "").strip()

        if not username:
            flash("Username is required.", "error")
            return redirect("/")

        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, phone, place) VALUES (%s, %s, %s)",
                    (username, phone, place),
                )
            flash("Data saved successfully!", "success")
        except pymysql.MySQLError as e:
            logging.exception("Insert failed: %s", e)
            flash(f"Failed to insert data into the database: {e}", "error")
        finally:
            try: conn.close()
            except: pass

        return redirect("/")

    # GET: list rows
    rows = []
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id, username, phone, place FROM users ORDER BY id DESC")
            rows = cur.fetchall()
    except pymysql.MySQLError as e:
        logging.exception("Select failed: %s", e)
        flash(f"Failed to fetch data from the database: {e}", "error")
    finally:
        try: conn.close()
        except: pass

    return render_template("form.html", rows=rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
