# Author(s): Pranjal Singh, Parth Patel
# This file contains the code that handles a user's session, such as login, logout
# and authenticating the user.


from flask import Flask, render_template, redirect, url_for, session, request
import database
from __main__ import website


@website.route('/login')
def login():
    return render_template('index.html')

@website.route('/welcome', methods=['GET', 'POST'])
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('password', None)
    return render_template('welcome.html')

@website.route('/dashboard', methods=['GET', 'POST'])
def authenticate_user():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if 'logged_in' in session:
        return render_template('manager_dashboard.html', msg=msg)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        cursor = database.conn.cursor()
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM Users WHERE Username=? AND Password=?', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            if account[6] == 1 or account[6] == 2:
                #Admin
                session['logged_in'] = True
                session['username'] = username
                session['password'] = password
                return render_template('manager_dashboard.html', msg=msg)
            else:
                #employee/basic user page
                return render_template('employee_dashboard.html', msg=msg)
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)