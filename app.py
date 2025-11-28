from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # change to anything random


# ---------- DATABASE SETUP ----------
def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_users_table():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            phone TEXT UNIQUE,
            password_hash BLOB
        )
    """)
    conn.commit()
    conn.close()


create_users_table()


# ---------- ROUTES: AUTH + PAGES ----------

@app.route("/")
def home():
    if "user_phone" in session:
        return render_template(
            "home.html",
            phone=session["user_phone"],
            username=session.get("username")
        )
    else:
        return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        phone = request.form["phone"]
        password = request.form["password"]

        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO users (username, phone, password_hash) VALUES (?, ?, ?)",
                (username, phone, password_hash)
            )
            conn.commit()
            conn.close()

            return render_template(
                "register.html",
                success="Registered successfully! Please login to continue."
            )

        except sqlite3.IntegrityError:
            conn.close()
            return render_template(
                "register.html",
                error="Phone number already registered."
            )

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form["phone"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
        conn.close()

        if user is None:
            # stay on LOGIN page and show error
            return render_template(
                "login.html",
                error="User not found. Please register to continue."
            )

        stored_hash = user["password_hash"]

        if bcrypt.checkpw(password.encode(), stored_hash):
            session["user_phone"] = phone
            session["username"] = user["username"]
            return redirect("/")
        else:
            # wrong password -> show error on LOGIN page
            return render_template(
                "login.html",
                error="Incorrect password. Try again."
            )

    # GET request -> just show login page
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_phone", None)
    session.pop("username", None)
    return redirect("/login")


# ---------- SIMPLE BOT LOGIC (CUSTOM REPLIES) ----------

def generate_bot_reply(message, username=None) -> str:
    # convert message to lowercase so case doesn't matter
    msg = message.lower().strip()
    name_part = username if username else "there"

    if not msg:
        return "I didn't receive any message. Can you type it again?"

    # ===== CUSTOM FRIEND REPLIES =====
    # this will match:
    # "tell me about rajkamal", "Tell me about Rajkamal", "WHO IS RAJ KAMAL?"
    if "rajkamal" in msg or "raj kamal" in msg:
        return (
            "Rajkamal — CSE (Data Science) student,"
"Founder & CEO of Alpha Talk 🚀,"
"Creative thinker, passionate learner,"
"Loves AI, coding & building futuristic products."
"A true leader with big dreams. 👑"

        )

    # you can edit these yourself later (placeholders for now):
    if "tell me about karthik" in msg:
        return "Karthik is an AIML student at Aditya University, a talented coder from Odisha, known for his dedication, sharp mind, and calm personality. 🚀"

    if "tell me about vishnu" in msg:
        return "No need to introduce Vishnu just ask anyone who is biryani boy ?? they will tell you about Vishnu"

    if "tell me about akshat" in msg:
        return "you mean keshri akshat ?/😂"

    if "tell me about danish" in msg:
        return " Danish bhaiii !!! Kyaaa Sirrrr (chatttt chattt)"

    if "tell me about abhay" in msg:
        return "student At aditya Engineering College"

    if "tell me about piyush" in msg:
        return " student At aditya Engineering College Piyush bhaiii !!! bhaii mera toh aakh fadak raha h"

    if "tell me about saudi" in msg:
        return "areeeeeeeeeeee madharch00d (exam time 9 se 10 ka bicch sab room m raid marne wala Saudi) chutt boy srry cute boy.."

    if "tell me about namit" in msg:
        return "tu tu tu tu tu Bakchodi kraga ?? isko koi kapda kharid ke do yaar pura hostal langte ghumta h"

    if "tell me about bikash" in msg:
        return "Thora room m aa na /// chl n bhuja bna n "

    if "tell me about anish" in msg:
        return " anish bhaii ke bare me kya he batuu yaar bhaii thora kha pii liya kr "

    if "tell me about aditya" in msg:
        return "aditya You mean Shreya wala kya ? accha ladka h bhaii bss chicken  nhi khata"

    if "tell me about dipendar" in msg:
        return "Dipu bhaii  ke bare me kya he btuu yaar (Neha wala n )?? iske bare m jada nhi pata"

    if "tell me about rahul" in msg:
        return " rahul bhaiya ke bare me kya he bolu bss bolunga bhaiya jii aap he movie dekhiye bawallllll h ekdam"
    if "tell me about arvind" in msg:
        return"Arvind is an AIML student from Kolkata, a good boy with a sharp mind, excellent coding skills, and a strong dedication to learning. 🚀"
    # ===== GENERAL REPLIES =====
    if any(x in msg for x in ["hello", "hi", "hey", "hii"]):
        return f"Hi {name_part}! 👋 How can I help you today?"

    if "exam" in msg or "test" in msg:
        return (
            "Exams can be stressful, but planning makes it easier.\n"
            "- Make a small timetable 📚\n"
            "- Solve previous year questions\n"
            "- Take short breaks and revise formulas\n"
            "Tell me your subject and I’ll suggest a quick study plan!"
        )

    if "python" in msg:
        return "Python is great! 🐍 Are you working on basics, data science, or web (Flask/Django)?"

    if "sad" in msg or "depress" in msg or "tired" in msg:
        return (
            "I’m sorry you’re feeling low 💙. Take a deep breath.\n"
            "Sometimes a short walk, music, or talking to a friend helps a lot.\n"
            "If it feels too heavy, please talk to someone you trust or a professional."
        )

    if "thank" in msg:
        return "You’re welcome! 😊 Anything else I can help you with?"

    # default fallback
    return (
        f'I heard: "{message}".\n'
        "Right now I’m using simple rules, but you can connect me to a real AI model later "
        "using an API inside this `/chat` route."
    )


# ---------- CHAT ROUTE (used by home.html JS) ----------

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True) or {}
    user_message = data.get("message", "")
    username = session.get("username")
    reply = generate_bot_reply(user_message, username)
    return jsonify({"reply": reply})


# ---------- MAIN ----------
if __name__ == "__main__":
    print("Starting Flask server at http://127.0.0.1:5000")
    app.run(debug=True)
