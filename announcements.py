# import smtplib as smtp, ssl
#
# import envs
# from email.mime.text import MIMEText
#
# def login():
#
#     subject = 'Test From Python'
#     body = 'Test from announcements.py'
#
#
#     port = 465
#     smtp_server = 'smtp.gmail.com'
#     password = input("Type your password and press enter: ")
#     sender_email = "seaviewrestauranttrainingtest1@gmail.com"
#     receiver_email = "parthpatel0422@gmail.com"
#
#     message = MIMEText(body, 'plain', 'utf-8')
#     message['Subject'] = subject
#     message['From'] = sender_email
#     message['To'] = ', '.join(receiver_email)
#
#     with smtp.SMTP(smtp_server, port) as server:
#         server.login(sender_email, password)
#         server.sendmail(sender_email, receiver_email, message.as_string())
#     print("Message sent!")

# The following code was acquired directly from Google's website itself
# I found it on https://developers.google.com/gmail/api/guides/sending#python
# import base64
# from email.message import EmailMessage
#
# import google.auth
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
#
#
# import os
#
# from google.oauth2 import service_account
# import googleapiclient.discovery  # type: ignore
#
# def create_key(service_account_email: str) -> None:
#     """Creates a key for a service account."""
#
#     credentials = service_account.Credentials.from_service_account_file(
#         filename=os.environ["GOOGLE_APPLICATION_CREDENTIALS"],
#         scopes=["https://www.googleapis.com/auth/cloud-platform"],
#     )
#
#     service = googleapiclient.discovery.build("iam", "v1", credentials=credentials)
#
#     key = (
#         service.projects()
#         .serviceAccounts()
#         .keys()
#         .create(name="projects/-/serviceAccounts/" + service_account_email, body={})
#         .execute()
#     )
#
#     # The privateKeyData field contains the base64-encoded service account key
#     # in JSON format.
#     # TODO(Developer): Save the below key {json_key_file} to a secure location.
#     #  You cannot download it again later.
#     # import base64
#     # json_key_file = base64.b64decode(key['privateKeyData']).decode('utf-8')
#
#     if not key["disabled"]:
#         print("Created json key")
#
#
# def gmail_create_draft():
#   """Create and insert a draft email.
#    Print the returned draft's message and id.
#    Returns: Draft object, including draft id and message meta data.
#
#   Load pre-authorized user credentials from the environment.
#   TODO(developer) - See https://developers.google.com/identity
#   for guides on implementing OAuth2 for the application.
#   """
#   creds, _ = google.auth.default()
#
#   try:
#     # create gmail api client
#     service = build("gmail", "v1", credentials=creds)
#
#     message = EmailMessage()
#
#     message.set_content("Sent from draft; test from announcements.py")
#
#     message["To"] = "parthpatel0422@gmail.com"
#     message["From"] = "seaviewrestauranttrainingtest1@gmail.com"
#     message["Subject"] = "Test From Python"
#
#     # encoded message
#     encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
#
#     create_message = {"message": {"raw": encoded_message}}
#     # pylint: disable=E1101
#     draft = (
#         service.users()
#         .drafts()
#         .create(userId="me", body=create_message)
#         .execute()
#     )
#
#     print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')
#
#   except HttpError as error:
#     print(f"An error occurred: {error}")
#     draft = None
#
#   return draft
#
#
#
#
# def gmail_send_message():
#   """Create and send an email message
#   Print the returned  message id
#   Returns: Message object, including message id
#
#   Load pre-authorized user credentials from the environment.
#   TODO(developer) - See https://developers.google.com/identity
#   for guides on implementing OAuth2 for the application.
#   """
#   creds, _ = google.auth.default()
#
#   try:
#     service = build("gmail", "v1", credentials=creds)
#     message = EmailMessage()
#
#     message.set_content("Sent from send; Test from announcements.py")
#
#     message["To"] = "parthpatel0422@gmail.com"
#     # message["From"] = "seaviewrestauranttrainingtest1@gmail.com"
#     message["From"] = "seaviewrestauranttrainingtest@seaviewrestauranttraining.iam.gserviceaccount.com"
#     message["Subject"] = "Test From Python"
#
#     # encoded message
#     encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
#
#     create_message = {"raw": encoded_message}
#     # pylint: disable=E1101
#     send_message = (
#         service.users()
#         .messages()
#         .send(userId="me", body=create_message)
#         .execute()
#     )
#     print(f'Message Id: {send_message["id"]}')
#   except HttpError as error:
#     print(f"An error occurred: {error}")
#     send_message = None
#   return send_message
#
# if __name__ == "__main__":
#     # create_key("seaviewrestauranttrainingtest1@gmail.com")
#     # create_key("seaviewrestauranttrainingtest@seaviewrestauranttraining.iam.gserviceaccount.com")
#     gmail_create_draft()
#     gmail_send_message()

import smtplib
import mailtrap

# def send_mail():
#     # sender = 'seaviewrestauranttraining1@gmail.com'
#     # receivers = ['parthpatel0422@gmail.com']
#     # message = """From: From Seaview Restaurant Training <seaviewrestauranttraining1@gmail.com>
#     # To: Parth Patel <parthpatel0422@gmail.com>
#     # Subject: Test
#     #
#     # This email was sent from Python
#     # """
#
#     # try:
#     #     smtpObj = smtplib.SMTP('localhost')
#     #     smtpObj.sendmail(sender, receivers, message)
#     #     print("Successfully sent email")
#     # except smtplib.SMTPException:
#     #     pass
#     #
#     mail = mailtrap.Mail(
#         sender=mailtrap.Address(email="seaviewrestauranttraining1@gmail.com", name="Seaview Restaurant Training Test"),
#         to=[mailtrap.Address(email="parthpatel0422@gmail.com")],
#         subject="Test",
#         text="This email was sent from Python"
#     )
#     client = mailtrap.MailtrapClient(token="ec7212d3cca28a491f84b005b659cef0")
#     client.send(mail)


import smtplib, ssl, sqlite3
def send_mail():
    port = 587
    smtp_server = "smtp.office365.com"
    sender_email = "seaviewrestauranttraining1@outlook.com"
    password = "seaviewrestaurant1"
    receiver_email = "parthpatel0422@gmail.com"
    message = """Subject: SMTP Test\n
    
    This email was sent from Python."""

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
        print("Email sent successfully")


def announcements():

    pass


if __name__ == "__main__":
    # send_mail()
    pass
