import os, random, sqlite3, time, secrets
from functools import wraps
from flask import (Flask, g, render_template, request, redirect,
                   url_for, session, flash, jsonify, abort)
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.environ.get("DB_PATH", "/data/app.db")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "change-me-now")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")

# ---------- Database ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(_):
    db = g.pop("db", None)
    if db:
        db.close()

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_admin INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        done INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """)
    if not db.execute("SELECT 1 FROM users WHERE username=?", (ADMIN_USERNAME,)).fetchone():
        db.execute("INSERT INTO users(username,password_hash,is_admin) VALUES(?,?,1)",
                   (ADMIN_USERNAME, generate_password_hash(ADMIN_PASSWORD)))
    db.commit(); db.close()

# ---------- Auth helpers ----------
def login_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if "uid" not in session:
            return redirect(url_for("login"))
        return f(*a, **kw)
    return wrapper

def admin_required(f):
    @wraps(f)
    @login_required
    def wrapper(*a, **kw):
        if not session.get("is_admin"):
            abort(403)
        return f(*a, **kw)
    return wrapper

def start_session(user):
    session.clear()
    session["uid"] = user["id"]
    session["username"] = user["username"]
    session["is_admin"] = bool(user["is_admin"])

# ---------- Anti-bot puzzle (verified on the server) ----------
@app.get("/puzzle/new")
def puzzle_new():
    nums = random.sample(range(1, 7), 6)           # 6 shuffled tiles
    session["puzzle"] = {"started": time.time(), "solved": False}
    return jsonify(tiles=nums)

@app.post("/puzzle/check")
def puzzle_check():
    p = session.get("puzzle")
    order = (request.get_json(silent=True) or {}).get("order")
    if not p or order != [1, 2, 3, 4, 5, 6] or time.time() - p["started"] < 1.5:
        session.pop("puzzle", None)
        return jsonify(ok=False), 400
    p["solved"] = True
    session["puzzle"] = p
    return jsonify(ok=True)

def puzzle_passed():
    p = session.pop("puzzle", None)
    return bool(p and p.get("solved"))

# ---------- Routes ----------
@app.get("/")
def index():
    return redirect(url_for("todos" if "uid" in session else "login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form.get("username", "").strip()
        pw = request.form.get("password", "")
        if not puzzle_passed():
            flash("Résous d'abord le puzzle.")
        elif not (3 <= len(u) <= 30) or not u.replace("_", "").isalnum():
            flash("Nom d'utilisateur : 3 à 30 caractères (lettres, chiffres, _).")
        elif len(pw) < 6:
            flash("Mot de passe : 6 caractères minimum.")
        else:
            db = get_db()
            try:
                cur = db.execute("INSERT INTO users(username,password_hash) VALUES(?,?)",
                                 (u, generate_password_hash(pw)))
                db.commit()
                start_session({"id": cur.lastrowid, "username": u, "is_admin": 0})
                return redirect(url_for("todos"))
            except sqlite3.IntegrityError:
                flash("Ce nom d'utilisateur existe déjà.")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username", "").strip()
        pw = request.form.get("password", "")
        user = get_db().execute("SELECT * FROM users WHERE username=?", (u,)).fetchone()
        if not puzzle_passed():
            flash("Résous d'abord le puzzle.")
        elif user and check_password_hash(user["password_hash"], pw):
            start_session(user)
            return redirect(url_for("admin" if user["is_admin"] else "todos"))
        else:
            flash("Identifiants incorrects.")
    return render_template("login.html")

@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/todos", methods=["GET", "POST"])
@login_required
def todos():
    db = get_db()
    if request.method == "POST":
        title = request.form.get("title", "").strip()[:200]
        if title:
            db.execute("INSERT INTO todos(user_id,title) VALUES(?,?)", (session["uid"], title))
            db.commit()
        return redirect(url_for("todos"))
    items = db.execute("SELECT * FROM todos WHERE user_id=? ORDER BY done, id DESC",
                       (session["uid"],)).fetchall()
    return render_template("todos.html", items=items)

@app.post("/todos/<int:tid>/toggle")
@login_required
def toggle(tid):
    db = get_db()
    db.execute("UPDATE todos SET done = 1-done WHERE id=? AND user_id=?", (tid, session["uid"]))
    db.commit()
    return redirect(url_for("todos"))

@app.post("/todos/<int:tid>/delete")
@login_required
def delete(tid):
    db = get_db()
    db.execute("DELETE FROM todos WHERE id=? AND user_id=?", (tid, session["uid"]))
    db.commit()
    return redirect(url_for("todos"))

@app.get("/admin")
@admin_required
def admin():
    db = get_db()
    users = db.execute("""SELECT u.id, u.username, u.created_at, u.is_admin,
                          (SELECT COUNT(*) FROM todos t WHERE t.user_id=u.id) AS n_todos
                          FROM users u ORDER BY u.created_at DESC""").fetchall()
    return render_template("admin.html", users=users, total=len(users))

init_db()
