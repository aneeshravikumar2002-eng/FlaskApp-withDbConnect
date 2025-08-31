import os
import logging
from flask import Flask, render_template, request, redirect, flash
import pymysql

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change_me")
app.debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"

# Env-driven DB config
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASS = os.getenv("DB_PASS", "appsecret")
DB_NAME = os.getenv("DB_NAME", "mydb")

DB_SSL_MODE = os.getenv("DB_SSL_MODE", "disabled")
DB_SSL_CA = os.getenv("DB_SSL_CA")

CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "5"))

logging.basicConfig(level=logging.INFO)


def _ssl_args():
    if DB_SSL_MODE.lower() == "required":
        if DB_SSL_CA and os.path.exists(DB_SSL_CA):
            return {"ssl": {"ca": DB_SSL_CA}}
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


def ensure_schema():
    """Create table if DB is reachable; ignore errors if not."""
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
        logging.warning("Could not ensure schema (DB not ready?): %s", e)


@app.route("/", methods=["GET", "POST"])
def index():
    db_connected = True
    rows = []

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
        except Exception as e:
            db_connected = False
            logging.warning("Insert failed (DB down?): %s", e)
            flash("Database not connected. Could not save data.", "error")
        finally:
            try:
                conn.close()
            except:
                pass

        return redirect("/")

    # GET: list rows if DB is up
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id, username, phone, place FROM users ORDER BY id DESC")
            rows = cur.fetchall()
    except Exception as e:
        db_connected = False
        logging.warning("Select failed (DB down?): %s", e)
    finally:
        try:
            conn.close()
        except:
            pass

    return render_template("form.html", rows=rows, db_connected=db_connected)


if __name__ == "__main__":
    # Try to set up schema, but don’t block startup if DB isn’t up
    with app.app_context():
        ensure_schema()

    app.run(host="0.0.0.0", port=5000)
