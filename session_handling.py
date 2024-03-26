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
                   'WHERE EMPLOYEE_ID=? AND QUIZ_ID IN (SELECT QUIZ_ID FROM QUIZZES WHERE IS_DELETED=0)'
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
    if total_questions == 0:
        percent = 0
    else:
        percent = total_correct / total_questions * 100
        percent = round(percent, 2)

    cursor.execute('SELECT * FROM QUIZZES WHERE QUIZ_ID NOT IN '
                   '(SELECT DISTINCT QUIZ_ID FROM ATTEMPT_HISTORY_LOG WHERE IS_COMPLETED=1 AND EMPLOYEE_ID=?) ', (session['id'],))
    quizzes = cursor.fetchall()

    cursor.execute('SELECT QUIZ_ID, QUIZ_NAME FROM QUIZZES ')

    quiz_list = []

    for _, quiz in cursor.fetchall():
        if quiz is not None:
            quiz_list.append(quiz)


    cursor.execute('SELECT NUM_CORRECT, NUM_INCORRECT, MAX(ATTEMPT_NUMBER) '
                   'FROM ATTEMPT_HISTORY_LOG '
                   'WHERE QUIZ_ID IN (SELECT DISTINCT QUIZ_ID FROM QUIZZES WHERE EMPLOYEE_ID=?) '
                   'GROUP BY QUIZ_ID ', (session['id'],))

    num_correct = []
    num_incorrect = []
    for correct, incorrect, _ in cursor.fetchall():
        if correct is not None:
            num_correct.append(correct)
        else:
            num_correct.append(0)
        if incorrect is not None:
            num_incorrect.append(incorrect)
        else:
            num_incorrect.append(0)

    return render_template('employee_dashboard.html', progress=total_correct, total_questions=total_questions, quizzes=quizzes, percent=percent, num_correct=num_correct, num_incorrect=num_incorrect, quiz_list=quiz_list)

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
            session['id'] = account[0]
            session['logged_in'] = True
            session['username'] = username
            session['password'] = password
            session['role'] = account[6]
            if session['role'] == 1 or session['role'] == 2:
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