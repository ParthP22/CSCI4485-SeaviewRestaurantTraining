# Author(s): Ahmed Malik
# This file contains the code that is used to view the history log,


import re
from flask import Flask, render_template, redirect, url_for, session, request
import database
from routes import website

def get_quiz_data():
    cursor = database.conn.cursor()
    cursor.execute('SELECT QUIZ_ID, QUESTION_ID, NUM_CORRECT, NUM_INCORRECT FROM QUESTIONS ORDER BY QUIZ_ID, QUESTION_ID')
    data = cursor.fetchall()
    return data



from collections import defaultdict
@website.route('/quiz_trends', methods=['GET', 'POST'])
def quiz_trends():
    data = get_quiz_data()
    quizzes = defaultdict(lambda: {'questions': [], 'num_correct': [], 'num_incorrect': []})

    for quiz_id, question_id, correct, incorrect in data:
        quiz = quizzes[quiz_id]
        quiz['questions'].append(question_id)
        quiz['num_correct'].append(correct)
        quiz['num_incorrect'].append(incorrect)

    return render_template('quiz_trends.html', quizzes=quizzes)
