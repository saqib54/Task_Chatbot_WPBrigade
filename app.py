from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import sqlite3
import re

app = Flask(__name__, template_folder="Templates", static_folder="static")
app.secret_key = "task_chatbot_vibe_secret_key"


# Database Connection Helper
def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create Database and Seed Initial Data
def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            city TEXT
        )
        """)

        # Initial seed users for auto-login & demo functionality
        seed_users = [
            ("Admin", "jhon.smith@xyz.com", "+92322", "Lahore"),
            ("Samantha", "samantha@xyz.com", "+14155552671", "Madrid"),
            ("Alex Johnson", "alex.j@xyz.com", "+447911123456", "London")
        ]

        for name, email, phone, city in seed_users:
            c.execute("""
            INSERT OR IGNORE INTO users(name, email, phone, city)
            VALUES(?, ?, ?, ?)
            """, (name, email, phone, city))

        conn.commit()


init_db()


def find_user_by_identifier(cursor, identifier):
    """
    Flexibly search for a user by email, exact name, or partial name/email prefix.
    Handles trailing possessives like "samanthas" -> "samantha".
    """
    clean_id = identifier.strip().strip('"').strip("'")
    
    # Strip possessives if any (e.g. samanthas -> samantha, samantha's -> samantha)
    if clean_id.lower().endswith("'s"):
        clean_id = clean_id[:-2]
    elif clean_id.lower().endswith("s") and not "@" in clean_id:
        # Check if without 's' matches a user first
        cursor.execute("SELECT * FROM users WHERE LOWER(name) = ?", (clean_id[:-1].lower(),))
        user = cursor.fetchone()
        if user:
            return user

    # 1. Exact Email Match
    cursor.execute("SELECT * FROM users WHERE LOWER(email) = ?", (clean_id.lower(),))
    user = cursor.fetchone()
    if user:
        return user

    # 2. Exact Name Match
    cursor.execute("SELECT * FROM users WHERE LOWER(name) = ?", (clean_id.lower(),))
    user = cursor.fetchone()
    if user:
        return user

    # 3. Email Prefix match (e.g. john.smith for john.smith@xyz.com)
    cursor.execute("SELECT * FROM users WHERE LOWER(email) LIKE ?", (f"{clean_id.lower()}%",))
    user = cursor.fetchone()
    if user:
        return user

    # 4. Partial Name match
    cursor.execute("SELECT * FROM users WHERE LOWER(name) LIKE ?", (f"%{clean_id.lower()}%",))
    user = cursor.fetchone()
    if user:
        return user

    return None


def format_name_from_email(email):
    prefix = email.split("@")[0]
    parts = re.split(r'[\._-]', prefix)
    return " ".join([p.capitalize() for p in parts if p])


# --- ROUTES ---

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email,))
            user = c.fetchone()
            
            if user:
                session["user"] = user["email"]
                session["user_name"] = user["name"]
                
                if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
                    return jsonify(success=True, redirect="/chat")
                return redirect("/chat")
            else:
                error_msg = f"Access Denied: '{email}' is not registered in the system."
                if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
                    return jsonify(success=False, message=error_msg), 401
                return render_template("login.html", error=error_msg)

    return render_template("login.html")


@app.route("/chat")
def chat():
    if "user" not in session:
        return redirect("/")
    return render_template("index.html", current_user=session.get("user"), user_name=session.get("user_name", "User"))


@app.route("/api/users", methods=["GET"])
def api_users():
    if "user" not in session:
        return jsonify(error="Unauthorized"), 401
        
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, email, phone, city FROM users ORDER BY id DESC")
        rows = c.fetchall()
        users = [dict(row) for row in rows]
    return jsonify(users=users)


@app.route("/message", methods=["POST"])
def message():
    if "user" not in session:
        return jsonify(reply="Session expired. Please log in again.", status="unauthorized"), 401

    payload = request.get_json(silent=True) or {}
    text = payload.get("message", "").strip()

    if not text:
        return jsonify(reply="Please enter a valid command.", status="error")

    with get_db() as conn:
        c = conn.cursor()

        # 1. ADD USER
        # E.g. can you add the user "john.smith@xyz.com" with phone number "+92332"
        # Or add user samantha@xyz.com with phone +1234 in city Cordoba
        if re.search(r'\b(add|create|register|insert)\b', text, re.I):
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+|\b[\w\.-]+@[\w\.-]+\b', text)
            phone_match = re.search(r'(?:phone|number|\+)?\s*["\']?(\+?\d[\d\s-]{3,15}\d|\+\d+)["\']?', text, re.I)
            
            # Extract optional explicit name if passed like name "John Smith"
            name_match = re.search(r'name\s*["\']([^"\'\n]+)["\']', text, re.I)
            
            # Extract optional city if passed like city "Cordoba" or in city Cordoba
            city_match = re.search(r'(?:city|in)\s*=?\s*["\']?([a-zA-Z\s]+?)["\']?(?:\s+with|\s+and|\s*$)', text, re.I)

            if email_match:
                email = email_match.group(0).lower().strip('"\'')
                
                # Determine phone
                phone = ""
                if phone_match:
                    phone = phone_match.group(1).strip()
                elif re.search(r'\+\d+', text):
                    phone = re.search(r'\+\d+', text).group(0)

                # Determine name
                name = name_match.group(1) if name_match else format_name_from_email(email)
                
                # Determine city
                city = ""
                if city_match and city_match.group(1).strip().lower() not in ["phone", "with", "number"]:
                    city = city_match.group(1).strip().capitalize()

                try:
                    c.execute(
                        "INSERT INTO users(name, email, phone, city) VALUES(?, ?, ?, ?)",
                        (name, email, phone, city)
                    )
                    conn.commit()
                    return jsonify(
                        reply=f"✅ User **{name}** (`{email}`) added successfully!",
                        action="user_added",
                        status="success",
                        user={"name": name, "email": email, "phone": phone, "city": city}
                    )
                except sqlite3.IntegrityError:
                    return jsonify(reply=f"⚠️ User with email **{email}** already exists in the system.", status="warning")
            else:
                return jsonify(reply="⚠️ Please specify a valid email address to add a user. Example: `add user \"john.smith@xyz.com\" with phone \"+92332\"`", status="warning")

        # 2. REMOVE USER
        # E.g. can you remove the user "john.smith@xyz.com"
        # Or remove user samantha
        if re.search(r'\b(remove|delete|drop)\b', text, re.I):
            # Extract email or search identifier
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+|\b[\w\.-]+@[\w\.-]+\b', text)
            
            target_user = None
            if email_match:
                target_email = email_match.group(0).lower().strip('"\'')
                c.execute("SELECT * FROM users WHERE LOWER(email) = ?", (target_email,))
                target_user = c.fetchone()
            else:
                # Try extracting name after "user" or "remove"
                id_match = re.search(r'(?:remove|delete|user)\s+["\']?([^"\'\n]+?)["\']?\s*$', text, re.I)
                if id_match:
                    target_user = find_user_by_identifier(c, id_match.group(1))

            if target_user:
                c.execute("SELECT COUNT(*) FROM users")
                total_users = c.fetchone()[0]
                if total_users <= 1 and target_user["email"] == session.get("user"):
                    return jsonify(reply="⚠️ Cannot remove the last remaining active system user.", status="warning")

                c.execute("DELETE FROM users WHERE id = ?", (target_user["id"],))
                conn.commit()
                return jsonify(
                    reply=f"🗑️ User **{target_user['name']}** (`{target_user['email']}`) has been removed.",
                    action="user_removed",
                    status="success"
                )
            else:
                return jsonify(reply="⚠️ Could not find a matching user to remove. Please check the email or name.", status="warning")

        # 3. UPDATE USER (CITY / PHONE / NAME)
        # E.g. can you update samanthas city to Cordoba
        # Or update john.smith@xyz.com phone to +92333
        if re.search(r'\b(update|change|set|modify)\b', text, re.I):
            # Check city update pattern
            city_update = re.search(r'update\s+(?:the\s+user\s+)?["\']?(.+?)["\']?\s+city\s+(?:to|=)\s+["\']?([^"\'\n\.]+?)["\']?$', text, re.I)
            alt_city = re.search(r'city\s+(?:of|for)\s+["\']?(.+?)["\']?\s+(?:to|=)\s+["\']?([^"\'\n\.]+?)["\']?$', text, re.I)
            generic_city = re.search(r'(.+?)(?:[\'’]s|\s+)\s*city\s+to\s+([a-zA-Z\s]+)$', text, re.I)

            target_id = None
            new_city = None

            if city_update:
                target_id = city_update.group(1)
                new_city = city_update.group(2).strip().capitalize()
            elif alt_city:
                target_id = alt_city.group(1)
                new_city = alt_city.group(2).strip().capitalize()
            elif generic_city:
                target_id = generic_city.group(1).replace("can you update", "").replace("update", "").strip()
                new_city = generic_city.group(2).strip().capitalize()

            if target_id and new_city:
                user = find_user_by_identifier(c, target_id)
                if user:
                    c.execute("UPDATE users SET city = ? WHERE id = ?", (new_city, user["id"]))
                    conn.commit()
                    return jsonify(
                        reply=f"✏️ Updated **{user['name']}**'s city to **{new_city}**.",
                        action="user_updated",
                        status="success"
                    )
                else:
                    return jsonify(reply=f"⚠️ User matching '{target_id}' was not found in the database.", status="warning")

            # Check phone update pattern
            phone_update = re.search(r'update\s+(?:the\s+user\s+)?["\']?(.+?)["\']?\s+phone\s+(?:to|=)\s+["\']?(\+?\d[\d\s-]{3,15}\d)["\']?$', text, re.I)
            if phone_update:
                target_id = phone_update.group(1)
                new_phone = phone_update.group(2).strip()
                user = find_user_by_identifier(c, target_id)
                if user:
                    c.execute("UPDATE users SET phone = ? WHERE id = ?", (new_phone, user["id"]))
                    conn.commit()
                    return jsonify(
                        reply=f"📞 Updated **{user['name']}**'s phone number to **{new_phone}**.",
                        action="user_updated",
                        status="success"
                    )
                else:
                    return jsonify(reply=f"⚠️ User matching '{target_id}' was not found in the database.", status="warning")

            return jsonify(reply="⚠️ Unrecognized update command format. Try: `can you update samanthas city to Cordoba`", status="warning")

        # 4. SHOW / LIST USERS
        if re.search(r'\b(show|list|view|display|all users|search)\b', text, re.I):
            c.execute("SELECT name, email, phone, city FROM users ORDER BY id ASC")
            rows = c.fetchall()
            if not rows:
                return jsonify(reply="📋 No users currently exist in the system database.", status="info")

            return jsonify(
                reply="Here are the currently registered system users:",
                action="list_users",
                users=[dict(row) for row in rows],
                status="success"
            )

        # 5. DEFAULT FALLBACK / HELP
        return jsonify(
            reply="💡 I didn't quite understand that command. Here are sample commands you can try:\n\n"
                  "• `can you add the user \"john.smith@xyz.com\" with phone number \"+92332\"`\n"
                  "• `can you update samanthas city to Cordoba`\n"
                  "• `can you remove the user \"john.smith@xyz.com\"`\n"
                  "• `show users`",
            status="info"
        )


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)