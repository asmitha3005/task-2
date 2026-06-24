from flask import Flask, render_template, request, redirect, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "ecommerce123"

def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        price REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cart(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        total REAL,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    conn.close()
    return render_template("home.html", products=products)

@app.route('/register', methods=['GET','POST'])
def register():

    if request.method=="POST":

        username=request.form['username']
        password=request.form['password']
        role=request.form['role']

        conn=sqlite3.connect("database.db")
        cur=conn.cursor()

        try:
            cur.execute(
            "INSERT INTO users(username,password,role) VALUES(?,?,?)",
            (username,password,role)
            )
            conn.commit()
            flash("Registration Successful")
            return redirect('/login')

        except:
            flash("Username already exists")

    return render_template("register.html")

@app.route('/login',methods=['GET','POST'])

def login():

    if request.method=="POST":

        username=request.form['username']
        password=request.form['password']

        conn=sqlite3.connect("database.db")
        cur=conn.cursor()

        cur.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username,password)
        )

        user=cur.fetchone()

        if user:
            session["user"]=user[0]
            session["role"]=user[3]

            if user[3]=="Admin":
                return redirect('/admin')

            return redirect('/')

        flash("Invalid Login")

    return render_template("login.html")

@app.route('/admin')
def admin():

    if session.get("role")!="Admin":
        return redirect('/')

    conn=sqlite3.connect("database.db")
    cur=conn.cursor()

    cur.execute("SELECT * FROM products")
    products=cur.fetchall()

    return render_template("admin.html",products=products)

@app.route('/add_product',methods=['POST'])

def add_product():

    if session.get("role")!="Admin":
        return redirect('/')

    name=request.form['name']
    description=request.form['description']
    price=request.form['price']

    conn=sqlite3.connect("database.db")
    cur=conn.cursor()

    cur.execute(
    "INSERT INTO products(name,description,price) VALUES(?,?,?)",
    (name,description,price)
    )

    conn.commit()

    return redirect('/admin')

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

if __name__=="__main__":
    app.run(debug=True)
