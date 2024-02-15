from flask import Flask, render_template, redirect, url_for, session, request
from flask_mysqldb import MySQL
import MySQLdb.cursors
# import sqlite3
app = Flask(__name__)

# conn = sqlite3.connect("Seaview_DB.db")
# cursor = conn.cursor()

app.config['MYSQL_HOST'] = 'sql5.freesqldatabase.com'
app.config['MYSQL_USER'] = 'sql5684251'
app.config['MYSQL_PASSWORD'] = 'nJzuzJDJ4D'
app.config['MYSQL_DB'] = 'sql5684251'

mysql = MySQL(app)


@app.route('/')
def welcome():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO USERS (USER_NAME, PASS_WORD, EMAIL) VALUES(%s, %s, %s)', ("test","test","testgmail",))
    cursor.execute('SELECT * FROM USERS')
    mysql.connection.commit()
    account = cursor.fetchone()
    name = account['USER_NAME']
    return render_template('welcome.html',name=name)







if __name__ == '__main__':
    # welcome()

    app.run(debug=True)