# Note from Parth: make sure you exclude this file whenever you push to GitHub from PyCharm.
# We don't want any merge conflicts.

import secrets
from flask import Flask, render_template

website = Flask(__name__)


# Note from Parth: I know PyCharm says that these imports aren't being used,
# but you actually need them in order to link the files together.
import announcements
import manage_employees
import session_handling
import manage_quizzes


# This will stay in app.py
def create_secret_key(length=32):
    return secrets.token_hex(length)

website.secret_key = create_secret_key()


# This will stay in app.py
@website.route('/')
def Welcome():
    return render_template('welcome.html')


if __name__ == '__main__':
    website.run(debug=True)