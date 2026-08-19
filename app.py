import random
import sqlite3
import os
from flask import Flask, g, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super_secret_hardware_key_2026")
DATABASE = "store.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def generate_electronics_inventory():
    IMAGE_POOLS = {
        "Storage": [
            "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=500",
            "https://images.unsplash.com/photo-1531492746076-161ca9bcad58?w=500",
            "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=500",
        ],
        "RAM Memory": [
            "https://images.unsplash.com/photo-1562976540-1502c2145186?w=500",
            "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=500",
        ],
        "Microcontrollers": [
            "https://images.unsplash.com/photo-1608564697071-ddf911d81370?w=500",
            "https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=500",
            "https://images.unsplash.com/photo-1555680202-c86f0e12f086?w=500",
        ],
        "Components & Robotics": [
            "https://images.unsplash.com/photo-1518770660439-4636190af475?w=500",
            "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=500",
            "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=500",
        ],
    }

    items = [
        ("Samsung 990 PRO NVMe M.2 SSD 1TB", 149.99, "Storage", IMAGE_POOLS["Storage"][0], "PCIe Gen4 x4 NVMe 2.0 with speeds up to 7450 MB/s read."),
        ("Kingston NV2 1TB PCIe 4.0 SSD", 64.99, "Storage", IMAGE_POOLS["Storage"][2], "Compact single-sided M.2 2280 form factor for ultra-fast storage."),
        ("Crucial MX500 500GB 2.5\" SATA SSD", 42.50, "Storage", IMAGE_POOLS["Storage"][0], "3D NAND technology with integrated power loss immunity."),
        ("Seagate Barracuda 2TB 3.5\" HDD", 54.99, "Storage", IMAGE_POOLS["Storage"][1], "7200 RPM desktop hard drive for massive data storage."),
        ("WD Black 4TB Performance Gaming HDD", 129.99, "Storage", IMAGE_POOLS["Storage"][1], "Dual-core processor architecture for faster game load times."),
        ("Corsair Vengeance RGB DDR5 32GB (2x16GB)", 119.99, "RAM Memory", IMAGE_POOLS["RAM Memory"][0], "Dynamic 10-zone RGB lighting with custom Intel XMP 3.0 profiles."),
        ("G.Skill Trident Z5 DDR5 64GB 6000MHz", 214.99, "RAM Memory", IMAGE_POOLS["RAM Memory"][1], "Ultra-high frequency performance engineered for extreme overclocking."),
        ("Kingston FURY Beast DDR4 16GB 3200MHz", 44.99, "RAM Memory", IMAGE_POOLS["RAM Memory"][0], "Low-profile heat spreader design compatible with most coolers."),
        ("Arduino Uno R4 WiFi Board", 27.50, "Microcontrollers", IMAGE_POOLS["Microcontrollers"][0], "RA4M1 32-bit ARM Cortex-M4 CPU with built-in ESP32-S3 WiFi & BT."),
        ("Raspberry Pi 5 (8GB RAM SBC)", 79.99, "Microcontrollers", IMAGE_POOLS["Microcontrollers"][1], "2.4GHz quad-core 64-bit Arm Cortex-A76 CPU with VideoCore VII GPU."),
        ("Raspberry Pi Pico W Microcontroller", 6.00, "Microcontrollers", IMAGE_POOLS["Microcontrollers"][2], "Dual-core Arm Cortex M0+ processor with 2.4GHz 802.11n wireless."),
        ("ESP32 WiFi + Bluetooth Dev Board", 8.50, "Microcontrollers", IMAGE_POOLS["Microcontrollers"][2], "Dual-core Tensilica LX6 SoC ideal for low-power IoT projects."),
        ("1/4W Resistor Kit (600 Pcs - Assorted)", 11.99, "Components & Robotics", IMAGE_POOLS["Components & Robotics"][2], "30 different resistance values from 10 ohm to 1M ohm."),
        ("16x2 LCD Display Module (Blue Backlight)", 5.50, "Components & Robotics", IMAGE_POOLS["Components & Robotics"][0], "HD44780 parallel interface display compatible with Arduino/Pi."),
        ("0.96 inch I2C OLED Display Module", 4.80, "Components & Robotics", IMAGE_POOLS["Components & Robotics"][1], "128x64 self-luminous white graphic display with SSD1306 driver."),
        ("Breadboard + Jumper Wires Starter Kit", 9.99, "Components & Robotics", IMAGE_POOLS["Components & Robotics"][1], "830 tie-point solderless breadboard with 65-piece jumper wire set."),
    ]

    storage_caps = ["256GB", "512GB", "1TB", "2TB"]
    ram_speeds = ["3200MHz", "3600MHz", "5200MHz", "6000MHz"]
    products = list(items)

    for cap in storage_caps:
        products.append((f"SanDisk Ultra SATA SSD {cap}", round(random.uniform(25, 180), 2), "Storage", random.choice(IMAGE_POOLS["Storage"]), f"High-speed {cap} solid state drive with read speeds up to 560MB/s."))

    for speed in ram_speeds:
        products.append((f"Corsair Vengeance LPX DDR4 {speed}", round(random.uniform(35, 120), 2), "RAM Memory", random.choice(IMAGE_POOLS["RAM Memory"]), f"Performance desktop memory kit operating at {speed} low latency."))

    for i in range(1, 35):
        products.append((f"Robotics Sensor Module Type-{i * 8}", round(random.uniform(2.5, 18.0), 2), "Components & Robotics", random.choice(IMAGE_POOLS["Components & Robotics"]), "High precision analog/digital sensor module for prototyping."))
        products.append((f"Arduino Expansion Shield v{i}.0", round(random.uniform(6.0, 28.0), 2), "Microcontrollers", random.choice(IMAGE_POOLS["Microcontrollers"]), "Multifunction expansion board with breakout pin headers."))

    return products


def init_db():
    with app.app_context():
        db = get_db()
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT NOT NULL,
                image_url TEXT,
                description TEXT
            );
            CREATE TABLE IF NOT EXISTS carts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            );
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total_amount REAL NOT NULL,
                shipping_address TEXT,
                payment_method TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders (id)
            );
        """)

        admin_pass = generate_password_hash("imtiaz3770")
        db.execute(
            """
            INSERT INTO users (username, password, is_admin)
            VALUES ('admin', ?, 1)
            ON CONFLICT(username) DO UPDATE SET password=?, is_admin=1
        """,
            (admin_pass, admin_pass),
        )

        cursor = db.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            db.executemany(
                "INSERT INTO products (name, price, category, image_url, description) VALUES (?, ?, ?, ?, ?)",
                generate_electronics_inventory(),
            )
        db.commit()

# Call database initialization on server startup
init_db()


# --- REST API ENDPOINTS ---

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username, password = data.get("username"), data.get("password")
    if not username or not password:
        return jsonify({"error": "Missing fields"}), 400

    db = get_db()
    hashed = generate_password_hash(password)
    try:
        db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        db.commit()
        return jsonify({"message": "Registered successfully!"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username taken"}), 400


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username, password = data.get("username"), data.get("password")
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    if user and check_password_hash(user["password"], password):
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["is_admin"] = user["is_admin"]
        return jsonify({
            "message": "Logged in",
            "user": {"username": user["username"], "is_admin": bool(user["is_admin"])},
        })
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@app.route("/api/me", methods=["GET"])
def me():
    if "user_id" in session:
        return jsonify({"logged_in": True, "username": session.get("username"), "is_admin": bool(session.get("is_admin"))})
    return jsonify({"logged_in": False, "is_admin": False})


@app.route("/api/products", methods=["GET"])
def get_products():
    category = request.args.get("category", "All")
    search = request.args.get("search", "")

    db = get_db()
    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if category != "All":
        query += " AND category = ?"
        params.append(category)
    if search:
        query += " AND name LIKE ?"
        params.append(f"%{search}%")

    query += " LIMIT 200"
    products = db.execute(query, params).fetchall()
    categories = db.execute("SELECT DISTINCT category FROM products").fetchall()
    return jsonify({"products": [dict(p) for p in products], "categories": [c["category"] for c in categories]})


@app.route("/api/cart", methods=["GET"])
def get_cart():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db()
    cart_items = db.execute(
        """
        SELECT c.id as cart_id, p.id as product_id, p.name, p.price, p.image_url, c.quantity, (p.price * c.quantity) as total
        FROM carts c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    """,
        (session["user_id"],),
    ).fetchall()
    return jsonify([dict(item) for item in cart_items])


@app.route("/api/cart/add", methods=["POST"])
def add_to_cart():
    if "user_id" not in session:
        return jsonify({"error": "Please log in to add items."}), 401

    data = request.get_json() or {}
    product_id, user_id = data.get("product_id"), session["user_id"]

    db = get_db()
    existing = db.execute("SELECT * FROM carts WHERE user_id = ? AND product_id = ?", (user_id, product_id)).fetchone()

    if existing:
        db.execute("UPDATE carts SET quantity = quantity + 1 WHERE id = ?", (existing["id"],))
    else:
        db.execute("INSERT INTO carts (user_id, product_id, quantity) VALUES (?, ?, 1)", (user_id, product_id))

    db.commit()
    return jsonify({"message": "Added to cart"})


@app.route("/api/cart/update", methods=["POST"])
def update_cart():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    cart_id, action = data.get("cart_id"), data.get("action")

    db = get_db()
    item = db.execute("SELECT * FROM carts WHERE id = ? AND user_id = ?", (cart_id, session["user_id"])).fetchone()

    if item:
        if action == "increase":
            db.execute("UPDATE carts SET quantity = quantity + 1 WHERE id = ?", (cart_id,))
        elif action == "decrease":
            if item["quantity"] > 1:
                db.execute("UPDATE carts SET quantity = quantity - 1 WHERE id = ?", (cart_id,))
            else:
                db.execute("DELETE FROM carts WHERE id = ?", (cart_id,))
        elif action == "delete":
            db.execute("DELETE FROM carts WHERE id = ?", (cart_id,))
        db.commit()

    return jsonify({"message": "Cart updated"})


@app.route("/api/checkout", methods=["POST"])
def checkout():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    full_name, address, card = data.get("full_name"), data.get("address"), data.get("card_number")

    if not full_name or not address or not card:
        return jsonify({"error": "Please complete all fields"}), 400

    db = get_db()
    user_id = session["user_id"]
    cart_items = db.execute(
        """
        SELECT c.quantity, p.name, p.price, (p.price * c.quantity) as total
        FROM carts c JOIN products p ON c.product_id = p.id WHERE c.user_id = ?
    """,
        (user_id,),
    ).fetchall()

    if not cart_items:
        return jsonify({"error": "Cart is empty"}), 400

    grand_total = sum(item["total"] for item in cart_items)
    shipping_info = f"{full_name}, {address}"
    masked_payment = f"Card ending in {card[-4:] if len(card) >= 4 else '****'}"

    cursor = db.execute(
        "INSERT INTO orders (user_id, total_amount, shipping_address, payment_method) VALUES (?, ?, ?, ?)",
        (user_id, grand_total, shipping_info, masked_payment),
    )
    order_id = cursor.lastrowid

    for item in cart_items:
        db.execute(
            "INSERT INTO order_items (order_id, product_name, price, quantity) VALUES (?, ?, ?, ?)",
            (order_id, item["name"], item["price"], item["quantity"]),
        )

    db.execute("DELETE FROM carts WHERE user_id = ?", (user_id,))
    db.commit()
    return jsonify({"message": "Order placed successfully!", "order_id": order_id})


@app.route("/api/orders", methods=["GET"])
def get_orders():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db()
    orders = db.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", (session["user_id"],)).fetchall()
    result = []

    for order in orders:
        items = db.execute("SELECT * FROM order_items WHERE order_id = ?", (order["id"],)).fetchall()
        result.append({
            "id": order["id"],
            "total": order["total_amount"],
            "shipping": order["shipping_address"],
            "payment": order["payment_method"],
            "date": order["created_at"],
            "items": [dict(i) for i in items],
        })

    return jsonify(result)


@app.route("/api/admin/products", methods=["POST"])
def admin_add_product():
    if not session.get("is_admin"):
        return jsonify({"error": "Access denied"}), 403

    data = request.get_json() or {}
    name = str(data.get("name", "")).strip()
    price = data.get("price")
    category = str(data.get("category", "")).strip()
    image_url = str(data.get("image_url", "")).strip() or "https://images.unsplash.com/photo-1518770660439-4636190af475?w=500"
    description = str(data.get("description", "")).strip() or "High quality electronic component."

    if not name or price is None or price == "" or not category:
        return jsonify({"error": "Please fill in Name, Price, and Category"}), 400

    try:
        price_val = float(price)
    except ValueError:
        return jsonify({"error": "Invalid price value"}), 400

    db = get_db()
    db.execute(
        "INSERT INTO products (name, price, category, image_url, description) VALUES (?, ?, ?, ?, ?)",
        (name, price_val, category, image_url, description),
    )
    db.commit()
    return jsonify({"message": "Product created successfully!"})


@app.route("/api/admin/products/<int:pid>", methods=["DELETE"])
def admin_delete_product(pid):
    if not session.get("is_admin"):
        return jsonify({"error": "Access denied"}), 403

    db = get_db()
    db.execute("DELETE FROM products WHERE id = ?", (pid,))
    db.commit()
    return jsonify({"message": "Product deleted."})


# --- FRONTEND UI ROUTE ---

@app.route("/")
def index():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEXUS Hardware & Robotics Store</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --bg-color: #f1f5f9;
            --text-color: #0f172a;
            --header-bg: #0f172a;
            --header-text: #ffffff;
            --card-bg: #ffffff;
            --card-border: #e2e8f0;
            --subtext: #64748b;
            --input-bg: #ffffff;
            --input-border: #cbd5e1;
            --admin-bg: #fefce8;
            --admin-border: #fde047;
            --badge-bg: #dbeafe;
            --badge-text: #1e40af;
        }

        body.dark-mode {
            --primary: #3b82f6;
            --primary-hover: #2563eb;
            --bg-color: #0b0f19;
            --text-color: #f8fafc;
            --header-bg: #111827;
            --header-text: #f8fafc;
            --card-bg: #1e293b;
            --card-border: #334155;
            --subtext: #94a3b8;
            --input-bg: #1e293b;
            --input-border: #475569;
            --admin-bg: #422006;
            --admin-border: #78350f;
            --badge-bg: #1e3a8a;
            --badge-text: #93c5fd;
        }

        * { box-sizing: border-box; }
        body { font-family: 'Inter', system-ui, sans-serif; margin: 0; background: var(--bg-color); color: var(--text-color); transition: background 0.2s, color 0.2s; }
        .top-banner { background: linear-gradient(90deg, #2563eb, #7c3aed); color: white; text-align: center; padding: 8px; font-size: 13px; font-weight: 600; letter-spacing: 0.5px; }

        header { background: var(--header-bg); color: var(--header-text); padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 90; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .logo { font-size: 22px; font-weight: 800; letter-spacing: -0.5px; display: flex; align-items: center; gap: 8px; }
        .logo span { color: #38bdf8; }
        
        .nav-actions { display: flex; align-items: center; gap: 10px; }
        .nav-actions input { padding: 8px 12px; border-radius: 6px; border: 1px solid var(--input-border); background: var(--input-bg); color: var(--text-color); font-size: 13px; }
        
        .btn-cart { position: relative; background: #334155; color: white; border: none; padding: 10px 18px; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 14px; display: flex; align-items: center; gap: 8px; }
        .cart-badge { position: absolute; top: -6px; right: -6px; background: #ef4444; color: white; border-radius: 50%; padding: 2px 7px; font-size: 11px; font-weight: bold; }

        .hero { background: var(--card-bg); border-bottom: 1px solid var(--card-border); padding: 40px 20px; text-align: center; }
        .hero h1 { font-size: 32px; margin: 0 0 10px 0; font-weight: 800; }
        .hero p { color: var(--subtext); max-width: 600px; margin: 0 auto; font-size: 15px; }

        .controls { max-width: 1200px; margin: 25px auto; padding: 0 20px; display: flex; gap: 15px; }
        .controls input, .controls select { padding: 12px 16px; border-radius: 8px; border: 1px solid var(--input-border); background: var(--input-bg); color: var(--text-color); font-size: 14px; outline: none; }
        .controls input { flex: 1; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }

        main { max-width: 1200px; margin: 0 auto; padding: 0 20px 60px; }
        
        .products-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 20px; }
        .product-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px; padding: 15px; display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.2s, box-shadow 0.2s; position: relative; overflow: hidden; }
        .product-card:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.08); }
        .product-img { width: 100%; height: 160px; object-fit: cover; border-radius: 8px; margin-bottom: 12px; cursor: pointer; }
        
        .category-badge { display: inline-block; background: var(--badge-bg); color: var(--badge-text); font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 4px; margin-bottom: 6px; text-transform: uppercase; width: fit-content; }
        .product-title { font-size: 14px; font-weight: 700; margin-bottom: 6px; height: 38px; overflow: hidden; cursor: pointer; line-height: 1.3; }
        .product-price { font-size: 18px; font-weight: 800; color: #10b981; margin-bottom: 12px; }
        
        .btn-primary { background: var(--primary); color: white; border: none; padding: 10px; border-radius: 6px; font-weight: 600; cursor: pointer; width: 100%; transition: background 0.15s; }
        .btn-primary:hover { background: var(--primary-hover); }
        .btn-danger { background: #ef4444; color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; }

        .cart-drawer-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: none; z-index: 100; backdrop-filter: blur(2px); }
        .cart-drawer { position: fixed; top: 0; right: -420px; width: 400px; height: 100%; background: var(--card-bg); box-shadow: -5px 0 25px rgba(0,0,0,0.2); z-index: 101; transition: right 0.3s ease; padding: 25px; display: flex; flex-direction: column; }
        .cart-drawer.open { right: 0; }
        .cart-items-container { flex: 1; overflow-y: auto; margin: 20px 0; }
        .cart-item { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--card-border); padding: 12px 0; }
        
        .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); display: none; justify-content: center; align-items: center; z-index: 120; }
        .modal { background: var(--card-bg); width: 500px; max-width: 90%; padding: 30px; border-radius: 12px; border: 1px solid var(--card-border); box-shadow: 0 15px 30px rgba(0,0,0,0.3); position: relative; }
        .modal input { width: 100%; padding: 10px; margin-bottom: 12px; border-radius: 6px; border: 1px solid var(--input-border); background: var(--input-bg); color: var(--text-color); }
        
        .toast { position: fixed; bottom: 20px; right: 20px; background: #0f172a; color: white; padding: 12px 24px; border-radius: 8px; display: none; border: 1px solid #334155; z-index: 200; font-weight: 500; }
        footer { background: var(--header-bg); color: var(--subtext); text-align: center; padding: 30px; font-size: 13px; margin-top: 60px; border-top: 1px solid var(--card-border); }
    </style>
</head>
<body>

    <div class="top-banner">⚡ FREE EXPRESS SHIPPING ON ALL ORDERS OVER $50 | 24/7 MAKER SUPPORT</div>

    <header>
        <div class="logo">⚡ NEXUS <span>HARDWARE</span></div>
        <div class="nav-actions">
            <button class="btn-cart" onclick="toggleTheme()" id="theme-btn" style="background:#334155;">🌙 Mode</button>
            <div id="auth-section"></div>
            <button class="btn-cart" onclick="toggleCartDrawer()">
                🛒 Cart
                <span class="cart-badge" id="cart-badge-count">0</span>
            </button>
        </div>
    </header>

    <div class="hero">
        <h1>Pro Electronics & Hardware Catalog</h1>
        <p>Direct supply of high-performance NVMe SSDs, DDR5 Memory, Microcontrollers, and Robotics Sensors.</p>
    </div>

    <div id="admin-section" style="max-width: 1200px; margin: 20px auto; padding: 20px; background: var(--admin-bg); border: 1px solid var(--admin-border); border-radius: 8px; display: none;">
        <h3>⚡ Admin Panel (restricted to admin)</h3>
        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            <input type="text" id="adm-name" placeholder="Component Name" style="padding: 8px; border-radius: 6px; border: 1px solid var(--input-border);">
            <input type="number" id="adm-price" placeholder="Price ($)" step="0.01" style="padding: 8px; border-radius: 6px; border: 1px solid var(--input-border);">
            <input type="text" id="adm-cat" placeholder="Category" style="padding: 8px; border-radius: 6px; border: 1px solid var(--input-border);">
            <input type="text" id="adm-icon" placeholder="Image URL (optional)" style="padding: 8px; border-radius: 6px; border: 1px solid var(--input-border);">
            <button class="btn-primary" onclick="adminAddProduct()" style="width: auto;">Add Component</button>
        </div>
    </div>

    <div class="controls">
        <input type="text" id="search-input" placeholder="Search 150+ products (e.g. SSD, DDR5, Arduino, Resistor...)" oninput="loadProducts()">
        <select id="category-select" onchange="loadProducts()"><option value="All">All Categories</option></select>
    </div>

    <main>
        <div class="products-grid" id="products-list"></div>
        
        <h2 style="margin-top: 50px;">Order Receipts & History</h2>
        <div id="orders-list" style="background: var(--card-bg); padding: 20px; border-radius: 12px; border: 1px solid var(--card-border);"><p style="color:var(--subtext);">Log in to view orders.</p></div>
    </main>

    <div class="cart-drawer-overlay" id="cart-overlay" onclick="toggleCartDrawer()"></div>
    <div class="cart-drawer" id="cart-drawer">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2 style="margin:0;">Your Cart</h2>
            <button onclick="toggleCartDrawer()" style="background:none; border:none; color:var(--text-color); font-size:20px; cursor:pointer;">✕</button>
        </div>
        <div class="cart-items-container" id="cart-list">Log in to view cart.</div>
        <div style="border-top: 1px solid var(--card-border); padding-top: 15px;">
            <h3 id="cart-total" style="display:flex; justify-content:space-between; margin-bottom: 15px;"><span>Total:</span> <span>$0.00</span></h3>
            <button class="btn-primary" onclick="openCheckoutModal()" style="background:#10b981; padding:14px; font-size:16px;">Proceed to Checkout ➔</button>
        </div>
    </div>

    <div id="quickview-modal" class="modal-overlay">
        <div class="modal">
            <button onclick="closeQuickView()" style="position:absolute; top:15px; right:15px; background:none; border:none; color:var(--text-color); font-size:20px; cursor:pointer;">✕</button>
            <img id="qv-img" src="" style="width:100%; height:200px; object-fit:cover; border-radius:8px; margin-bottom:15px;">
            <span id="qv-cat" class="category-badge"></span>
            <h2 id="qv-title" style="margin: 5px 0 10px 0; font-size: 18px;"></h2>
            <p id="qv-desc" style="color: var(--subtext); font-size: 14px; line-height: 1.5;"></p>
            <div id="qv-price" class="product-price"></div>
            <button id="qv-add-btn" class="btn-primary">Add to Cart</button>
        </div>
    </div>

    <div id="checkout-modal" class="modal-overlay">
        <div class="modal">
            <h3>💳 Checkout Payment</h3>
            <label><small>Full Name</small></label>
            <input type="text" id="chk-name" placeholder="Imtiaz Ahmed">
            
            <label><small>Shipping Address</small></label>
            <input type="text" id="chk-address" placeholder="123 Tech Avenue, Suite 4">
            
            <label><small>Card Number</small></label>
            <input type="text" id="chk-card" placeholder="4532 •••• •••• 8892">
            
            <div style="display: flex; gap: 10px;">
                <div style="flex: 1;">
                    <label><small>Expiry</small></label>
                    <input type="text" id="chk-exp" placeholder="MM/YY">
                </div>
                <div style="flex: 1;">
                    <label><small>CVV</small></label>
                    <input type="password" id="chk-cvv" placeholder="123" maxlength="4">
                </div>
            </div>

            <div style="display:flex; justify-content:flex-end; gap:10px; margin-top:15px;">
                <button onclick="closeCheckoutModal()" style="padding: 10px 18px; border-radius: 6px; border: 1px solid var(--input-border); background: var(--input-bg); color: var(--text-color); cursor: pointer;">Cancel</button>
                <button class="btn-primary" onclick="submitOrder()" style="background:#10b981; width: auto;">Confirm & Pay</button>
            </div>
        </div>
    </div>

    <div id="toast" class="toast"></div>

    <footer>
        <p>© 2026 NEXUS Hardware Corp. All rights reserved. Encrypted SSL 256-bit Connection.</p>
    </footer>

    <script>
        let isAdmin = false;

        function initTheme() {
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme === 'dark') {
                document.body.classList.add('dark-mode');
                document.getElementById('theme-btn').innerText = '☀️ Mode';
            }
        }

        function toggleTheme() {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            document.getElementById('theme-btn').innerText = isDark ? '☀️ Mode' : '🌙 Mode';
        }

        function toggleCartDrawer() {
            const drawer = document.getElementById('cart-drawer');
            const overlay = document.getElementById('cart-overlay');
            const isOpen = drawer.classList.contains('open');
            
            if (isOpen) {
                drawer.classList.remove('open');
                overlay.style.display = 'none';
            } else {
                drawer.classList.add('open');
                overlay.style.display = 'block';
            }
        }

        function showToast(msg) {
            const t = document.getElementById('toast');
            t.innerText = msg; t.style.display = 'block';
            setTimeout(() => t.style.display = 'none', 2500);
        }

        async function checkAuth() {
            const res = await fetch('/api/me');
            const data = await res.json();
            const authSection = document.getElementById('auth-section');
            isAdmin = data.is_admin;

            document.getElementById('admin-section').style.display = isAdmin ? 'block' : 'none';

            if (data.logged_in) {
                authSection.innerHTML = `
                    <span style="font-size:13px;">User: <b>${data.username}</b> ${isAdmin ? '<b style="color:#f59e0b">(ADMIN)</b>' : ''}</span>
                    <button class="btn-danger" onclick="logout()">Logout</button>
                `;
                loadCart(); loadOrders();
            } else {
                authSection.innerHTML = `
                    <input type="text" id="username" placeholder="Username" size="8">
                    <input type="password" id="password" placeholder="Password" size="8">
                    <button class="btn-primary" style="padding:6px 12px; width:auto; font-size:12px;" onclick="login()">Login</button>
                    <button style="padding:6px 12px; border-radius:6px; border:1px solid #475569; background:#334155; color:white; font-size:12px; cursor:pointer;" onclick="register()">Register</button>
                `;
                document.getElementById('cart-list').innerHTML = 'Log in to view cart.';
                document.getElementById('orders-list').innerHTML = '<p style="color:var(--subtext);">Log in to view orders.</p>';
            }
            loadProducts();
        }

        async function login() {
            const u = document.getElementById('username').value;
            const p = document.getElementById('password').value;
            const res = await fetch('/api/login', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: u, password: p})
            });
            const data = await res.json();
            if (res.ok) { checkAuth(); showToast("Logged in successfully!"); } else { alert(data.error); }
        }

        async function register() {
            const u = document.getElementById('username').value;
            const p = document.getElementById('password').value;
            const res = await fetch('/api/register', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: u, password: p})
            });
            const data = await res.json();
            showToast(data.message || data.error);
        }

        async function logout() {
            await fetch('/api/logout', {method: 'POST'});
            checkAuth();
        }

        let allLoadedProducts = [];

        async function loadProducts() {
            const search = document.getElementById('search-input').value;
            const cat = document.getElementById('category-select').value;
            const res = await fetch(`/api/products?search=${search}&category=${cat}`);
            const data = await res.json();
            allLoadedProducts = data.products;

            const catSelect = document.getElementById('category-select');
            const currentCat = catSelect.value;
            catSelect.innerHTML = '<option value="All">All Categories</option>' + 
                data.categories.map(c => `<option value="${c}" ${c===currentCat?'selected':''}>${c}</option>`).join('');

            const container = document.getElementById('products-list');
            container.innerHTML = data.products.map(p => `
                <div class="product-card">
                    <div>
                        <img src="${p.image_url}" class="product-img" onclick="openQuickView(${p.id})" alt="product">
                        <span class="category-badge">${p.category}</span>
                        <div class="product-title" onclick="openQuickView(${p.id})">${p.name}</div>
                    </div>
                    <div>
                        <div class="product-price">$${p.price.toFixed(2)}</div>
                        <button class="btn-primary" onclick="addToCart(${p.id})">Add to Cart</button>
                        ${isAdmin ? `<button class="btn-danger" style="width:100%; margin-top:5px;" onclick="adminDeleteProduct(${p.id})">Delete (Admin)</button>` : ''}
                    </div>
                </div>
            `).join('');
        }

        function openQuickView(pid) {
            const p = allLoadedProducts.find(item => item.id === pid);
            if (!p) return;
            document.getElementById('qv-img').src = p.image_url;
            document.getElementById('qv-cat').innerText = p.category;
            document.getElementById('qv-title').innerText = p.name;
            document.getElementById('qv-desc').innerText = p.description || 'High performance electronic component designed for stability and fast throughput.';
            document.getElementById('qv-price').innerText = '$' + p.price.toFixed(2);
            document.getElementById('qv-add-btn').onclick = () => { addToCart(p.id); closeQuickView(); };
            document.getElementById('quickview-modal').style.display = 'flex';
        }

        function closeQuickView() {
            document.getElementById('quickview-modal').style.display = 'none';
        }

        async function addToCart(pid) {
            const res = await fetch('/api/cart/add', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({product_id: pid})
            });
            const data = await res.json();
            if (res.ok) { loadCart(); showToast("Added to cart!"); } else { alert(data.error); }
        }

        async function updateCart(cartId, action) {
            await fetch('/api/cart/update', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({cart_id: cartId, action: action})
            });
            loadCart();
        }

        async function loadCart() {
            const res = await fetch('/api/cart');
            if (!res.ok) return;
            const cart = await res.json();
            const container = document.getElementById('cart-list');

            let totalQty = 0;
            cart.forEach(item => totalQty += item.quantity);
            document.getElementById('cart-badge-count').innerText = totalQty;

            if (cart.length === 0) {
                container.innerHTML = '<p style="color:var(--subtext);">Your cart is empty.</p>';
                document.getElementById('cart-total').innerHTML = '<span>Total:</span> <span>$0.00</span>';
                return;
            }

            let sum = 0;
            container.innerHTML = cart.map(i => {
                sum += i.total;
                return `
                    <div class="cart-item">
                        <div style="flex:1;">
                            <b style="font-size:13px; display:block;">${i.name}</b>
                            <small style="color:var(--subtext);">$${i.price.toFixed(2)} each</small>
                        </div>
                        <div style="display:flex; align-items:center; gap:6px;">
                            <button class="btn-danger" style="padding:2px 6px;" onclick="updateCart(${i.cart_id}, 'decrease')">-</button>
                            <span>${i.quantity}</span>
                            <button class="btn-primary" style="padding:2px 6px; width:auto;" onclick="updateCart(${i.cart_id}, 'increase')">+</button>
                            <span style="font-weight:bold; width:60px; text-align:right;">$${i.total.toFixed(2)}</span>
                        </div>
                    </div>
                `;
            }).join('');
            document.getElementById('cart-total').innerHTML = `<span>Total:</span> <span>$${sum.toFixed(2)}</span>`;
        }

        function openCheckoutModal() {
            toggleCartDrawer();
            document.getElementById('checkout-modal').style.display = 'flex';
        }

        function closeCheckoutModal() {
            document.getElementById('checkout-modal').style.display = 'none';
        }

        async function submitOrder() {
            const full_name = document.getElementById('chk-name').value;
            const address = document.getElementById('chk-address').value;
            const card_number = document.getElementById('chk-card').value;

            const res = await fetch('/api/checkout', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ full_name, address, card_number })
            });

            const data = await res.json();
            if (res.ok) {
                closeCheckoutModal();
                showToast("Order Confirmed! Receipt created.");
                loadCart(); loadOrders();
            } else { alert(data.error); }
        }

        async function loadOrders() {
            const res = await fetch('/api/orders');
            if (!res.ok) return;
            const orders = await res.json();
            const container = document.getElementById('orders-list');

            if (orders.length === 0) {
                container.innerHTML = '<p style="color:var(--subtext);">No past orders found.</p>';
                return;
            }

            container.innerHTML = orders.map(o => `
                <div style="border-bottom: 1px solid var(--card-border); padding-bottom: 12px; margin-bottom: 12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b>Order #${o.id}</b>
                        <span style="color:#10b981; font-weight:bold;">$${o.total.toFixed(2)}</span>
                    </div>
                    <small style="color:var(--subtext)">📍 ${o.shipping || 'N/A'} | 💳 ${o.payment || 'N/A'} | 📅 ${o.date}</small><br>
                    <small><b>Items:</b> ${o.items.map(i => `${i.product_name} (x${i.quantity})`).join(', ')}</small>
                </div>
            `).join('');
        }

        async function adminAddProduct() {
            const name = document.getElementById('adm-name').value;
            const price = document.getElementById('adm-price').value;
            const category = document.getElementById('adm-cat').value;
            const image_url = document.getElementById('adm-icon').value;

            const res = await fetch('/api/admin/products', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ name, price, category, image_url })
            });

            const data = await res.json();
            if (res.ok) {
                showToast("Product Created!");
                loadProducts();
            } else { alert(data.error); }
        }

        async function adminDeleteProduct(pid) {
            if (!confirm("Delete product?")) return;
            const res = await fetch(`/api/admin/products/${pid}`, {method: 'DELETE'});
            if (res.ok) { showToast("Product Deleted"); loadProducts(); }
        }

        initTheme();
        checkAuth();
    </script>
</body>
</html>
    """


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
