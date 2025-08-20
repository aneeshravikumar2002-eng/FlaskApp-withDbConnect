from flask import Flask, render_template, request, redirect
import pymysql

app = Flask(__name__)

# Update with your RDS DB details
DB_HOST = "your-rds-endpoint"
DB_USER = "admin"
DB_PASS = "yourpassword"
DB_NAME = "mydb"

def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form["username"]
        phone = request.form["phone"]
        place = request.form["place"]

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, phone, place) VALUES (%s, %s, %s)",
                    (username, phone, place))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/")

    conn = get_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT id, username, phone, place FROM users ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("form.html", rows=rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
