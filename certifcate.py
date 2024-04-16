import re
from flask import Flask, render_template, redirect, url_for, session, request
import database
from routes import website

def generate_certificate():
    cursor = database.conn.cursor()
    cursor.execute('SELECT First_Name, Last_Name FROM Users WHERE Username=? AND Password=?', (session['username'], session['password'],))
    user_profile = cursor.fetchone()
    return render_template('certificate.html', user_profile=user_profile)

import smtplib
import ssl
import credentials
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
def send_certificate():
    # First, generate the certificate HTML
    html_content = generate_certificate()  # Ensure this function returns HTML as a string

    # SMTP server configuration
    port = 587  # For SSL
    smtp_server = "smtp.office365.com"
    sender_email = credentials.email
    receiver_email = session['email']
    password = credentials.password

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Create the email message
    message = MIMEMultipart("alternative")
    message["Subject"] = "Certificate of Completion"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Turn the HTML into a MIMEText object
    part = MIMEText(html_content, "html")
    message.attach(part)

    # Send the email
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)  # Secure the connection
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())