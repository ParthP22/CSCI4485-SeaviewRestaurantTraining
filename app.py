from flask import Flask, render_template, request, redirect

app = Flask(__name__)


# @app.route('/')
# def hello_world():  # put application's code here
#     return 'Hello World!'

@app.route('/')
def render_page():
    return render_template('home.html')


if __name__ == '__main__':
    app.run()
