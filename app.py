import secrets
from flask import Flask, render_template

app = Flask(__name__)


# Note from Parth: I know PyCharm says that these imports aren't being used,
# but you actually need them in order to link the files together.
import announcements
import manage_employees
import session_handling


# This will stay in app.py
def create_secret_key(length=32):
    return secrets.token_hex(length)

app.secret_key = create_secret_key()


# This will stay in app.py
@app.route('/')
def Welcome():
    return render_template('welcome.html')


if __name__ == '__main__':
    app.run(debug=True)