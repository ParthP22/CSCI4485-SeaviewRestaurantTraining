# Author(s): Parth Patel
# This file contains the code that is required to be able to successfully send an email
# through seaviewrestauranttraining@outlook.com on the announcements page.
import datetime
from datetime import date

from flask import Flask, render_template, redirect, url_for, session, request
import database, smtplib, ssl, credentials, datetime
from routes import website

# This one is used for the announcements function
def send_mail(subject, body):
    cursor = database.conn.cursor()
    cursor.execute('SELECT Email FROM Users WHERE ID >= 1 AND ID <= 4')
    receiver_emails = cursor.fetchall()
    port = 587
    smtp_server = "smtp.office365.com"
    sender_email = credentials.email
    password = credentials.password
    message = f"""Subject: {subject}\n
{body}"""

    context = ssl.create_default_context()
    for receiver_email in receiver_emails:
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
    print("Email sent successfully")



@website.route('/announcements', methods=['GET', 'POST'])
def announcements():
    cursor = database.conn.cursor()
    # If account exists in accounts table in out database

    username = session['username']
    password = session['password']
    cursor.execute('SELECT * FROM Users WHERE Username=? AND Password=?', (username, password,))
    account = cursor.fetchone()
    if account[6] == 1 or account[6] == 2:
        # Admin
        status = "Type your message"
        if request.method == 'POST' and 'subject' in request.form and 'body' in request.form:

            subject = request.form['subject']
            body = request.form['body']
            send_mail(subject, body)
            status = "Email sent successfully"
            cursor.execute('SELECT MAX(MESSAGE_ID) FROM ANNOUNCEMENTS')
            query = cursor.fetchone()
            curr_message_id = 0
            if query[0] is not None:
                curr_message_id = query[0]
            cursor.execute('INSERT INTO ANNOUNCEMENTS(MESSAGE_ID, SUBJECT, MESSAGE, DATE_TIME) VALUES (?, ?, ?, ?)', (curr_message_id + 1,subject,body,datetime.datetime.now(),))
            database.conn.commit()
            # return redirect(url_for('announcements'))
            return render_template('announcements.html', status=status)

        else:
            return render_template('announcements.html', status=status)

    else:
        # employee/basic user page
        cursor.execute('SELECT SUBJECT,MESSAGE,DATE_TIME FROM ANNOUNCEMENTS ORDER BY MESSAGE_ID DESC')
        emails = cursor.fetchall()
        return render_template('announcements_history.html', emails=emails)


