# Author(s): Parth Patel

import datetime
from datetime import date

from flask import Flask, render_template, redirect, url_for, session, request
import database, smtplib, ssl, credentials, datetime
from routes import website


# This is for after you submit a quiz
def send_report():
    pass

# This is for the manager dashboard
@website.route('/progress_report/<int:user_id>', methods=['GET'])
def send_report(user_id):
    cursor = database.conn.cursor()
    cursor.execute('SELECT m.EMAIL FROM USERS u LEFT JOIN USERS m on u.MANAGER_ID = m.ID WHERE u.ID=? ',(user_id,))
    manager_email = cursor.fetchone()[0]
    if manager_email is not None:

        subject="Test Report"
        body="Testing"
        send_mail(subject,body,manager_email)
    return redirect('/manage_employee')


# This one is used for the report function
def send_mail(subject, body, recipient_email):

    port = 587
    smtp_server = "smtp.office365.com"
    sender_email = credentials.email
    password = credentials.password
    message = f"""Subject: {subject}\n
{body}"""

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient_email, message)
    print("Email sent successfully")