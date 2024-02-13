from flask import Flask, render_template, redirect, url_for, session, request
import sqlite3
app = Flask(__name__)

conn = sqlite3.connect("Seaview_DB.db")
cursor = conn.cursor()

@app.route('/')
def welcome():
    return render_template('welcome.html')







if __name__ == '__main__':
    app.run(debug=True)