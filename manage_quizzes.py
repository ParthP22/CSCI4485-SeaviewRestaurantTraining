# Author(s): Ryan Minneo, Ryan Nguyen
# This file contains the code that is used to manage quizzes,
# such as being able to register new quizzes, edit existing quizzes, and delete quizzes if need be.

from flask import Flask, render_template, redirect, url_for, session, request
import database
from routes import website

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
    return render_template('quiz_editor.html')

@website.route('/take_quiz', methods=['GET'])
def take_quiz():
    # Retrieve quiz ID from the request URL
    quiz_id = request.args.get('id')

    # Connect to SQLite database
    conn = database.conn

    # Fetch quiz details from the database
    cursor = conn.cursor()
    cursor.execute("SELECT QUIZ_NAME, QUIZ_DESC FROM QUIZZES WHERE QUIZ_ID = ?", (quiz_id,))
    quiz_info = cursor.fetchone()  # Assuming only one row will be returned
    quiz_name, quiz_desc = quiz_info if quiz_info else (None, None)

    # Fetch questions for the specified quiz from the database
    cursor.execute(
        "SELECT QUESTION_ID, QUESTION, ANSWER_A, ANSWER_B, ANSWER_C, ANSWER_D, CORRECT_ANSWER FROM QUESTIONS WHERE QUIZ_ID = ?",
        (quiz_id,))
    questions = []
    for row in cursor.execute(
            "SELECT QUESTION_ID, QUESTION, ANSWER_A, ANSWER_B, ANSWER_C, ANSWER_D, CORRECT_ANSWER FROM QUESTIONS WHERE QUIZ_ID = ?",
            (quiz_id,)):
        question_id, question_text, answer_a, answer_b, answer_c, answer_d, correct_answer = row
        options = [
            {'option_id': 1, 'option_text': answer_a},
            {'option_id': 2, 'option_text': answer_b},
            {'option_id': 3, 'option_text': answer_c},
            {'option_id': 4, 'option_text': answer_d}
        ]
        questions.append({'id': question_id, 'question_text': question_text, 'options': options})

    cursor.close()

    # Render the template with quiz details and questions
    return render_template('take_quiz.html', quiz_name=quiz_name, quiz_desc=quiz_desc, questions=questions)

@website.route('/quiz_editing', methods=['GET', 'POST'])
def quiz_editing():
    count = 0
    file_data = None  # Define file_data variable outside the conditional block
    # Check if the quiz name, quiz description, and material name is inputted into their text boxes.
    if request.method == 'POST' and 'quiz_name' in request.form and 'quiz_desc' in request.form and 'material_name' in request.form:
        # Retrieve data from the HTML form
        quiz_name = request.form['quiz_name']
        quiz_desc = request.form['quiz_desc']
        material_name = request.form['material_name']

        # Retrieve questions and answers dynamically
        questions = []
        for key, value in request.form.items():
            if key.startswith('question'):
                question_number = key.replace('question', '')
                question = {
                    'QUESTION': value,
                    'ANSWER_A': request.form[f'option{question_number}A'],
                    'ANSWER_B': request.form[f'option{question_number}B'],
                    'ANSWER_C': request.form[f'option{question_number}C'],
                    'ANSWER_D': request.form[f'option{question_number}D'],
                    'CORRECT_ANSWER': request.form[f'correctAnswer{question_number}']
                }
                count = count + 1
                questions.append(question)

        cursor = database.conn.cursor()
        cursor.execute('INSERT INTO QUIZZES (QUIZ_NAME, TOTAL_QUESTIONS, TOTAL_CORRECT, TOTAL_INCORRECT, IS_VISIBLE, QUIZ_DESC, IS_DELETED) VALUES (?, ?, ?, ?, ?, ?, ?)', (quiz_name, count, 0, 0, 1, quiz_desc, 0))

        #Gets the ID from the quiz that was just created to upload that into the questions that are created.
        cursor.execute('SELECT MAX(QUIZ_ID) FROM QUIZZES')
        quizID = cursor.fetchone()[0]

        #Uploads questions into the database
        for question in questions:
            cursor.execute('''INSERT INTO QUESTIONS (QUIZ_ID, QUESTION, ANSWER_A, ANSWER_B, ANSWER_C, ANSWER_D, 
            CORRECT_ANSWER, NUM_CORRECT, NUM_INCORRECT, NUM_EMPLOYEES_COMPLETED, QUESTION_TYPE)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (quizID, question['QUESTION'], question['ANSWER_A'], question['ANSWER_B'],
                           question['ANSWER_C'], question['ANSWER_D'], question['CORRECT_ANSWER'], 0, 0, 0, "Multiple Choice"))

        # Retrieve data for pdf images
        # Handle file upload
        if request.method == 'POST':
            # Check if the file is present in the request
            if 'file' in request.files:
                file = request.files['file']
                file_data = file.read() # Assign value to file_data variable if 'file' is present
                if file_data is not None:
                    cursor.execute('INSERT INTO TRAINING_MATERIALS (MATERIAL_NAME, MATERIAL_BYTES, QUIZ_ID) VALUES (?, ?, ?)',(material_name, file_data, quizID))



        # Commit changes to the database
        database.conn.commit()

    return redirect(url_for('manage_quizzes'))

@website.route('/deleteQuiz/<int:quiz_id>', methods=['GET'])
def deleteQuiz_route(quiz_id):
    cursor = database.conn.cursor()
    cursor.execute("UPDATE QUIZZES SET IS_DELETED = 1 WHERE QUIZ_ID=?", (quiz_id,))
    database.conn.commit()

    return redirect(url_for('manage_quizzes'))

