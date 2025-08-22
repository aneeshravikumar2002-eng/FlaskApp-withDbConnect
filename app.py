from flask import Flask, render_template, request, redirect, flash
import pymysql
import logging

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flash messages
app.debug = True  # Enable debug mode for detailed error messages

# Update with your RDS DB details
DB_HOST = "your-rds-endpoint"
DB_USER = "admin"
DB_PASS = "yourpassword"
DB_NAME = "mydb"

def get_connection():
    try:
        return pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
    except pymysql.MySQLError as e:
        logging.error(f"Database connection error: {e}")
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form["username"]
        phone = request.form["phone"]
        place = request.form["place"]

        conn = get_connection()
        if conn is None:
            flash("Failed to connect to the database. Data not saved.", "error")
            return redirect("/")

        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, phone, place) VALUES (%s, %s, %s)",
                        (username, phone, place))
            conn.commit()
            flash("Data saved successfully!", "success")
        except pymysql.MySQLError as e:
            logging.error(f"Database query error: {e}")
            flash("Failed to insert data into the database.", "error")
        finally:
            cur.close()
            conn.close()
        return redirect("/")

    conn = get_connection()
    if conn is None:
        flash("Failed to connect to the database.", "error")
        return render_template("form.html", rows=[])

    try:
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT id, username, phone, place FROM users ORDER BY id DESC")
        rows = cur.fetchall()
    except pymysql.MySQLError as e:
        logging.error(f"Database query error: {e}")
        rows = []
        flash("Failed to fetch data from the database.", "error")
    finally:
        cur.close()
        conn.close()
    return render_template("form.html", rows=rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
