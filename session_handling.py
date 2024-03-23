# Author(s): Pranjal Singh, Parth Patel
# This file contains the code that handles a user's session, such as login, logout
# and authenticating the user.


from flask import Flask, render_template, redirect, url_for, session, request
import database
from routes import website


@website.route('/login')
def login():
    return render_template('index.html')

@website.route('/welcome', methods=['GET', 'POST'])
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('password', None)
    return render_template('welcome.html')

def render_employee_dashboard(account, cursor):
    cursor.execute('SELECT NUM_CORRECT, NUM_INCORRECT, MAX(ATTEMPT_NUMBER) '
                   'FROM ATTEMPT_HISTORY_LOG '
                   'WHERE EMPLOYEE_ID=? '
                   'GROUP BY QUIZ_ID',
                   (account[0],))
    recent_attempts = cursor.fetchall()
    total_correct = 0
    total_questions = 0
    # cursor.execute('SELECT QUIZ_ID FROM QUIZZES')
    # total_quizzes = cursor.fetchall()
    # total_correct = 0
    # total_questions = 0
    # if total_quizzes is not NoneType:
    #     for quiz in total_quizzes:
    #         cursor.execute(
    #             'SELECT NUM_CORRECT, NUM_INCORRECT, MAX(ATTEMPT_NUMBER) FROM ATTEMPT_HISTORY_LOG WHERE EMPLOYEE_ID=? AND QUIZ_ID=?',
    #             (account[0], quiz[0]))
    #         progress = cursor.fetchone()
    #         total_correct += progress[0]
    #         total_questions += progress[0] + progress[1]

    if recent_attempts is not None:
        for attempt in recent_attempts:
            total_correct += attempt[0]
            total_questions += attempt[0] + attempt[1]

    return render_template('employee_dashboard.html', progress=total_correct, total_questions=total_questions)

@website.route('/dashboard', methods=['GET', 'POST'])
def authenticate_user():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    account = None
    cursor = database.conn.cursor()

    if 'logged_in' in session:
        cursor.execute('SELECT * FROM Users WHERE Username=? AND Password=?', (session['username'],session['password']))
        account = cursor.fetchone()
        if account[6] == 1 or account[6] == 2:
            return render_template('manager_dashboard.html')
        else:
            return render_employee_dashboard(account,cursor)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using SQLite
        cursor.execute('SELECT * FROM Users WHERE Username=? AND Password=?', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            session['logged_in'] = True
            session['username'] = username
            session['password'] = password
            if account[6] == 1 or account[6] == 2:
                #Admin
                return render_template('manager_dashboard.html', msg=msg)
            else:
                #employee/basic user page

                return render_employee_dashboard(account,cursor)
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)