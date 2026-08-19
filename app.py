from flask import Flask, render_template, request, redirect, url_for, session
import os
import sqlite3

# 1. INITIALIZE FLASK APP AT TOP LEVEL
app = Flask(__name__)
app.secret_key = "nexushardware"

# 2. YOUR DATABASE INITIALIZATION FUNCTION & CALL
def init_db():
    # Put your REAL database creation code here (tables, admin account, etc.)
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    # ... your CREATE TABLE statements ...
    conn.commit()
    conn.close()

# Initialize the database immediately when Render loads the app
init_db()

# 3. ALL YOUR ROUTES
@app.route("/")
def home():
    # Put your REAL home route code here
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # Put your REAL login route code here
    pass

# ... (Paste all remaining @app.route functions from your original code here) ...

# 4. LOCAL RUN FALLBACK AT THE VERY BOTTOM
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
