# Author(s): Pranjal Singh
# This file contains the code that is used to manage employee accounts,
# such as being able to register new employees.

import re
import smtplib
import ssl

from flask import Flask, render_template, redirect, url_for, session, request

import credentials
import database
from routes import website


@website.route('/register_employee')
def register_employee():

    cursor = database.conn.cursor()

    cursor.execute('SELECT * FROM Roles ')
    roles = cursor.fetchall()

    return render_template('register_employee.html', roles = roles)

@website.route('/manage_employee')
def manage_employee():
    cursor = database.conn.cursor()

    cursor.execute('SELECT u.ID, u.USERNAME, u.FIRST_NAME, u.LAST_NAME, u.EMAIL, r.ROLE_NAME, u.MANAGER_ID, m.FIRST_NAME, m.LAST_NAME '
                   'FROM Users u JOIN Roles r ON u.ROLE_ID = r.ID LEFT JOIN Users m  ON u.MANAGER_ID = m.ID')
    users = cursor.fetchall()



    return render_template('manage_employee.html', users = users)


@website.route('/registration', methods=['GET', 'POST'])
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
        cursor = database.conn.cursor()
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
            database.conn.commit()
            msg = 'You have successfully registered!'

            cursor.execute('SELECT * FROM Users ')
            users = cursor.fetchall()
            return render_template('manage_employee.html', users=users)


    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register_employee.html', msg=msg)

def delete_item(item_id):
    cursor = database.conn.cursor()
    cursor.execute("DELETE FROM Users WHERE id=?", (item_id,))
    database.conn.commit()

@website.route('/delete/<int:item_id>', methods=['GET'])
def delete_route(item_id):
    delete_item(item_id)
    return redirect(url_for('manage_employee'))