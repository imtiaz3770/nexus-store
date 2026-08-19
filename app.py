from flask import Flask, render_template_string, request, redirect, url_for, session
import os
import sqlite3

# 1. INITIALIZE FLASK APP AT TOP LEVEL
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "nexus_super_secret_key_123")

# 2. INLINE HTML TEMPLATES (No separate templates folder needed)
HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>NEXUS Store</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #0f172a; color: #f8fafc; }
        .container { max-width: 800px; margin: auto; background: #1e293b; padding: 20px; border-radius: 8px; }
        h1 { color: #38bdf8; }
        a { color: #38bdf8; text-decoration: none; }
        .nav { margin-bottom: 20px; }
        .product { border: 1px solid #334155; padding: 15px; margin-bottom: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to NEXUS Hardware Store</h1>
        <div class="nav">
            {% if session.get('logged_in') %}
                <p>Logged in as: <strong>{{ session.get('username') }}</strong> | <a href="/logout">Logout</a></p>
            {% else %}
                <a href="/login">Login</a>
            {% endif %}
        </div>
        <h2>Available Products</h2>
        {% for product in products %}
            <div class="product">
                <h3>{{ product[1] }}</h3>
                <p>Price: ${{ product[2] }}</p>
            </div>
        {% endfor %}
    </div>
</body>
</html>
"""

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>NEXUS Store - Login</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #0f172a; color: #f8fafc; }
        .container { max-width: 400px; margin: auto; background: #1e293b; padding: 20px; border-radius: 8px; }
        h1 { color: #38bdf8; }
        input { width: 100%; padding: 10px; margin: 8px 0; box-sizing: border-box; }
        button { width: 100%; padding: 10px; background: #0284c7; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .error { color: #ef4444; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Admin Login</h1>
        {% if error %}<p class="error">{{ error }}</p>{% endif %}
        <form method="POST">
            <label>Username</label>
            <input type="text" name="username" required>
            <label>Password</label>
            <input type="password" name="password" required>
            <button type="submit">Log In</button>
        </form>
    </div>
</body>
</html>
"""

# 3. DATABASE INITIALIZATION
def init_db():
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO products (name, price) VALUES ('NEXUS RTX 4090 GPU', 1599.99)")
        cursor.execute("INSERT INTO products (name, price) VALUES ('NEXUS Mechanical Keyboard', 129.99)")
    conn.commit()
    conn.close()

# Run database setup immediately so Render initializes SQLite on boot
init_db()

# 4. ROUTES
@app.route("/")
def home():
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return render_template_string(HOME_HTML, products=products)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "imtiaz3770":
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("home"))
        else:
            error = "Invalid credentials. Please try again."
    return render_template_string(LOGIN_HTML, error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# 5. LOCAL RUN FALLBACK
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
