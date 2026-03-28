from flask import Flask, render_template, request, redirect, session, jsonify
import os
from db import get_db, query_format
from recommender import get_movies, recommend_from_favorites
import bcrypt

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret123")

# ---------------- INIT DB ----------------
def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS favorites(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        movie TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = bcrypt.hashpw(request.form["password"].encode(), bcrypt.gensalt())

        conn = get_db()
        c = conn.cursor()
        c.execute(query_format("INSERT INTO users(username,password) VALUES (?,?)"), (u,p))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"].encode()

        conn = get_db()
        c = conn.cursor()
        c.execute(query_format("SELECT password FROM users WHERE username=?"), (u,))
        user = c.fetchone()
        conn.close()

        if user and bcrypt.checkpw(p, user[0]):
            session["user"] = u
            return redirect("/")

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# ---------------- HOME ----------------
@app.route("/", methods=["GET"])
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html", movies=[])

# ---------------- API MOVIES ----------------
@app.route("/get-movies", methods=["POST"])
def get_movies_api():
    emotion = request.form.get("emotion")
    search = request.form.get("search")
    action = request.form.get("action")

    if action == "search":
        movies = get_movies(None, search)
    else:
        movies = get_movies(emotion, None)

    return jsonify(movies)

# ---------------- SAVE ----------------
@app.route("/save", methods=["POST"])
def save():
    if "user" not in session:
        return redirect("/login")

    movie = request.form["movie"]
    user = session["user"]

    conn = get_db()
    c = conn.cursor()
    c.execute(query_format("INSERT INTO favorites(username,movie) VALUES (?,?)"), (user,movie))
    conn.commit()
    conn.close()

    return redirect("/")

# ---------------- REMOVE ----------------
@app.route("/remove/<movie>")
def remove(movie):
    if "user" not in session:
        return redirect("/login")

    user = session["user"]

    conn = get_db()
    c = conn.cursor()
    c.execute(query_format("DELETE FROM favorites WHERE username=? AND movie=?"), (user,movie))
    conn.commit()
    conn.close()

    return redirect("/favorites")

# ---------------- FAVORITES ----------------
@app.route("/favorites")
def favorites():
    if "user" not in session:
        return redirect("/login")

    user = session["user"]

    conn = get_db()
    c = conn.cursor()
    c.execute(query_format("SELECT movie FROM favorites WHERE username=?"), (user,))
    data = [x[0] for x in c.fetchall()]
    conn.close()

    return render_template("favorites.html", movies=data)

# ---------------- AI RECOMMEND ----------------
@app.route("/ai-recommend")
def ai_recommend():
    if "user" not in session:
        return redirect("/login")

    user = session["user"]
    movies = recommend_from_favorites(user)

    return render_template("index.html", movies=movies)

# ---------------- RUN ----------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)