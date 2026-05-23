from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "student_secret"

# ================= DATABASE CONNECTION =================

def get_db_connection():

    conn = sqlite3.connect('student.db')

    conn.row_factory = sqlite3.Row

    return conn

# ================= CREATE TABLES =================

def create_tables():

    conn = get_db_connection()

    cur = conn.cursor()

    # USERS TABLE

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # STUDENTS TABLE

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        course TEXT,
        marks INTEGER
    )
    """)

    conn.commit()

    conn.close()

create_tables()

# ================= CREATE DEFAULT ADMIN =================

def create_admin():

    conn = get_db_connection()

    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username=?",
        ('admin',)
    )

    user = cur.fetchone()

    if not user:

        hashed_password = generate_password_hash('admin123')

        cur.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            ('admin', hashed_password)
        )

        conn.commit()

    conn.close()

create_admin()

# ================= LOGIN =================

@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user['password'], password):

            session['user'] = username

            flash("Login Successful")

            return redirect('/dashboard')

        else:

            flash("Invalid Username or Password")

    return render_template('login.html')

# ================= REGISTER =================

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if user:

            flash("Username Already Exists")

            return redirect('/register')

        conn.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, hashed_password)
        )

        conn.commit()

        conn.close()

        flash("Registration Successful")

        return redirect('/')

    return render_template('register.html')

# ================= DASHBOARD =================

@app.route('/dashboard')
def dashboard():

    if 'user' not in session:

        return redirect('/')

    conn = get_db_connection()

    students = conn.execute(
        "SELECT * FROM students"
    ).fetchall()

    conn.close()

    return render_template(
        'dashboard.html',
        students=students,
        total_students=len(students)
    )

# ================= ADD STUDENT =================

@app.route('/add', methods=['POST'])
def add_student():

    if 'user' not in session:

        return redirect('/')

    name = request.form['name']
    email = request.form['email']
    course = request.form['course']
    marks = request.form['marks']

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO students(name,email,course,marks)
        VALUES(?,?,?,?)
    """, (name, email, course, marks))

    conn.commit()

    conn.close()

    flash("Student Added Successfully")

    return redirect('/dashboard')

# ================= DELETE STUDENT =================

@app.route('/delete/<int:id>')
def delete_student(id):

    if 'user' not in session:

        return redirect('/')

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM students WHERE id=?",
        (id,)
    )

    conn.commit()

    conn.close()

    flash("Student Deleted Successfully")

    return redirect('/dashboard')

# ================= EDIT STUDENT =================

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):

    if 'user' not in session:

        return redirect('/')

    conn = get_db_connection()

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        course = request.form['course']
        marks = request.form['marks']

        conn.execute("""
            UPDATE students
            SET name=?, email=?, course=?, marks=?
            WHERE id=?
        """, (name, email, course, marks, id))

        conn.commit()

        conn.close()

        flash("Student Updated Successfully")

        return redirect('/dashboard')

    student = conn.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        'edit_student.html',
        student=student
    )

# ================= LOGOUT =================

@app.route('/logout')
def logout():

    session.pop('user', None)

    flash("Logged Out Successfully")

    return redirect('/')

# ================= RUN APP =================

if __name__ == '__main__':

    app.run(debug=True)