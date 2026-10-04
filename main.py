from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import getpass

app = Flask(__name__)
app.secret_key = "secretkey"

# Ask the person running the program for their MySQL password
mysql_password = getpass.getpass("Enter your MySQL password: ")

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password=mysql_password
)

cursor = db.cursor()

# Create the database if it does not already exist
cursor.execute("CREATE DATABASE IF NOT EXISTS login_system")
cursor.execute("USE login_system")

# Create the users table if it does not already exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
)
""")

db.commit()


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s",
            (username, password)
        )

        account = cursor.fetchone()

        if account:
            session["username"] = username
            return redirect(url_for("index"))
        else:
            message = "Incorrect username or password."

    return render_template("login.html", message=message)


@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM users WHERE username = %s",
            (username,)
        )

        account = cursor.fetchone()

        if account:
            message = "Account already exists."

        elif username == "" or password == "":
            message = "Please fill out the form."

        else:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )

            db.commit()
            return redirect(url_for("login"))

    return render_template("register.html", message=message)


@app.route("/index")
def index():
    if "username" in session:
        return render_template(
            "index.html",
            username=session["username"]
        )

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
