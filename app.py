from flask import Flask, render_template, request, redirect, session, jsonify
import os
from db import get_db, query_format
from recommender import get_movies, recommend_from_favorites
from ml_recommender import data
import bcrypt
from dotenv import load_dotenv

load_dotenv() 

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=True
)

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        username TEXT,
        password TEXT
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS favorites(
        id SERIAL PRIMARY KEY,
        username TEXT,
        movie TEXT
    )
    """)
    conn.commit()
    conn.close()
init_db()

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        raw_password = request.form["password"]
        hashed = bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()
        conn = get_db()
        c = conn.cursor()
        c.execute(query_format("INSERT INTO users(username,password) VALUES (?,?)"), (u, hashed))
        conn.commit()
        conn.close()
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        raw_password = request.form["password"]
        conn = get_db()
        c = conn.cursor()
        c.execute(query_format("SELECT password FROM users WHERE username=?"), (u,))
        user = c.fetchone()
        conn.close()

        if user:
            stored_password = user[0]
            try:
                if isinstance(stored_password, str):
                    stored_password = stored_password.encode()
                if bcrypt.checkpw(raw_password.encode(), stored_password):
                    session["user"] = u
                    return redirect("/")
            except:
                return "Password format error (old data). Please register again."
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")
    
@app.route("/", methods=["GET"])
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html", movies=[])

@app.route("/get-movies", methods=["POST"])
def get_movies_api():
    emotion = request.form.get("emotion")
    search = request.form.get("search")
    print("SEARCH:", search)
    print("EMOTION:", emotion)
    if search and search.strip():
        movies = get_movies(None, search) 
    elif emotion:
        movies = get_movies(emotion, None)  
    else:
        movies = get_movies() 
    return jsonify(movies)

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

@app.route("/ai-recommend")
def ai_recommend():
    if "user" not in session:
        return redirect("/login")
    user = session["user"]
    movies = recommend_from_favorites(user) or []
    # print("AI recommended movies:", movies)
    return render_template("index.html", movies=movies)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)