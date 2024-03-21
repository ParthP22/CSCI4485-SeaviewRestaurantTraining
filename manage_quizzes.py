# Author(s): Ryan Minneo
# This file contains the code that is used to manage quizzes,
# such as being able to register new quizzes, edit existing quizzes, and delete quizzes if need be.

import re
from flask import Flask, render_template, redirect, url_for, session, request
import database
from __main__ import website

@website.route('/manage_quizzes')
def manage_quizzes():
    cursor = database.conn.cursor()

    cursor.execute('SELECT * FROM QUIZZES')
    quizzes = cursor.fetchall()
    return render_template('manage_quizzes.html', quizzes = quizzes)

#Routes quiz list to the quiz editor
@website.route('/quiz_editor')
def quiz_editor():
    cursor = database.conn.cursor()

