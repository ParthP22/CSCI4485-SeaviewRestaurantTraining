# Author(s): Ryan Minneo, Ryan Nguyen
# This file contains the code that is allow the employee to take quizzes

from flask import Flask, render_template, redirect, url_for, session, request
import database
from routes import website


@website.route('/take_quiz')
def index():
    # Connect to SQLite database
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    # Fetch questions from the database
    cursor.execute("SELECT id, question_text FROM questions")
    questions = []
    for row in cursor.fetchall():
        question_id, question_text = row
        cursor.execute("SELECT id, option_text FROM options WHERE question_id = ?", (question_id,))
        options = [{'id': option_id, 'option_text': option_text} for option_id, option_text in cursor.fetchall()]
        questions.append({'id': question_id, 'question_text': question_text, 'options': options})

    conn.close()

    return render_template('quiz_template.html', questions=questions)


if __name__ == '__main__':
    app.run(debug=True)