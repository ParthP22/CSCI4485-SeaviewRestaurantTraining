# Author(s): Parth Patel
# This file contains the code that is required to be able to successfully send an email
# through seaviewrestauranttraining@outlook.com on the announcements page.

from flask import Flask, render_template, redirect, url_for, session, request
import database, smtplib, ssl, credentials
from routes import website

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
    status = "Type your message"
    if request.method == 'POST' and 'subject' in request.form and 'body' in request.form:

        subject = request.form['subject']
        body = request.form['body']
        send_mail(subject, body)
        status = "Email sent successfully"
        # return redirect(url_for('announcements'))
        return render_template('announcements.html', status=status)

    else:
        return render_template('announcements.html', status=status)

