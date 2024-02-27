import re

from flask import Flask, render_template, redirect, url_for, session, request
import sqlite3
app = Flask(__name__)

def connect_db():
    conn = sqlite3.connect("Seaview_DB.db")
    return conn

@app.route('/')
def Welcome():
    return render_template('welcome.html')

@app.route('/login')
def login():
    return render_template('index.html')

@app.route('/register_employee')
def register_employee():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Roles ')
    roles = cursor.fetchall()

    return render_template('register_employee.html', roles = roles)


@app.route('/manage_employee')
def manage_employee():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Users ')
    users = cursor.fetchall()
    return render_template('manage_employee.html', users = users)

@app.route('/', methods=['GET', 'POST'])
def authenticate_user():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        conn = connect_db()
        cursor = conn.cursor()
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM Users WHERE Username=? AND Password=?', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:

            if account[6] == 1 or account[6] == 2:
                #Admin
                conn.close()
                return render_template('manager_dashboard.html', msg=msg)
            else:
                #employee/basic user page
                conn.close()
                return 'Logged in successfully! Employee/Basic'
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    conn.close()
    return render_template('index.html', msg=msg)

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form\
    and 'first_name' in request.form and 'last_name' in request.form:
        # Create variables for easy access
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role_id = request.form.get('role')

        # Check if account exists using MySQL
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE Username=?', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO Users (username, first_name, last_name, password, email, role_id) VALUES ( ?, ?, ?, ?, ?, ?)',
                           (username, first_name, last_name, password, email, role_id))
            conn.commit()
            msg = 'You have successfully registered!'

            cursor.execute('SELECT * FROM Users ')
            users = cursor.fetchall()
            return render_template('manage_employee.html', users=users)


    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)





if __name__ == '__main__':
    app.run(debug=True)