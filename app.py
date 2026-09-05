from flask import Flask, jsonify, request, send_from_directory, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/index.html")
def index_page():
    return send_from_directory(".", "index.html")


@app.route("/category.html")
def category_page():
    return send_from_directory(".", "category.html")


@app.route("/offers.html")
def offers_page():
    return send_from_directory(".", "offers.html")


@app.route("/contact.html")
def contact_page():
    return send_from_directory(".", "contact.html")


@app.route("/login.html")
def login_page():
    return send_from_directory(".", "login.html")


@app.route("/register.html")
def register_page():
    return send_from_directory(".", "register.html")


@app.route("/image/<path:filename>")
def image_files(filename):
    return send_from_directory("image", filename)


@app.route("/public/<path:filename>")
def public_files(filename):
    return send_from_directory("public", filename)


@app.route("/api/health")
def health():
    try:
        connection = get_db_connection()
        connection.close()

        return jsonify({
            "status": "ok",
            "message": "Flask and MySQL are connected"
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    subject = data.get("subject", "").strip()
    message = data.get("message", "").strip()

    if not name or not email or not message:
        return jsonify({
            "success": False,
            "message": "Name, email and message are required"
        }), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO contacts (name, email, subject, message)
            VALUES (%s, %s, %s, %s)
            """,
            (name, email, subject, message)
        )

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "message": "Your message has been sent successfully!"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Database error: " + str(e)
        }), 500


@app.route("/api/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    email = data.get("email", "").strip()

    if not email:
        return jsonify({
            "success": False,
            "message": "Email is required"
        }), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO subscribers (email) VALUES (%s)",
            (email,)
        )

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "message": "Successfully subscribed!"
        })

    except mysql.connector.IntegrityError:
        return jsonify({
            "success": False,
            "message": "This email is already subscribed."
        }), 409

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Database error: " + str(e)
        }), 500


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({
            "success": False,
            "message": "All fields are required"
        }), 400

    if len(password) < 6:
        return jsonify({
            "success": False,
            "message": "Password must contain at least 6 characters"
        }), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        if cursor.fetchone():
            cursor.close()
            connection.close()

            return jsonify({
                "success": False,
                "message": "This email is already registered."
            }), 409

        hashed_password = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s)
            """,
            (name, email, hashed_password)
        )

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "message": "Account created successfully!"
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Database error: " + str(e)
        }), 500


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required"
        }), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, name, email, password
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if not user or not check_password_hash(
            user["password"],
            password
        ):
            return jsonify({
                "success": False,
                "message": "Invalid email or password."
            }), 401

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]

        return jsonify({
            "success": True,
            "message": "Login successful!",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Database error: " + str(e)
        }), 500


@app.route("/api/current-user")
def current_user():
    if "user_id" not in session:
        return jsonify({
            "logged_in": False
        })

    return jsonify({
        "logged_in": True,
        "user": {
            "id": session["user_id"],
            "name": session["user_name"],
            "email": session["user_email"]
        }
    })


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({
        "success": True,
        "message": "Logged out successfully!"
    })


if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
