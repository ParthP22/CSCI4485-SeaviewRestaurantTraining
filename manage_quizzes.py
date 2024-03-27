# Author(s): Ryan Minneo, Ryan Nguyen
# This file contains the code that is used to manage quizzes,
# such as being able to register new quizzes, edit existing quizzes, and delete quizzes if need be.
import datetime
import io
import smtplib

from flask import Flask, render_template, redirect, url_for, session, request
import database
import send_reports
from routes import website
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage



@website.route('/manage_quizzes')
def manage_quizzes():
    if session['role'] == 1 or session['role'] == 2:
        cursor = database.conn.cursor()

        cursor.execute('SELECT * FROM QUIZZES')
        quizzes = cursor.fetchall()
        return render_template('manage_quizzes.html', quizzes = quizzes)
    else:
        return render_template('prohibited.html')

#Routes quiz list to the quiz editor
@website.route('/quiz_editor')
def quiz_editor():
    if session['role'] == 1 or session['role'] == 2:
        quiz_id = request.args.get('quiz_id')
        quiz_name = request.args.get('quiz_name')
        quiz_desc = request.args.get('quiz_desc')

        cursor = database.conn.cursor()

        # Fetch all questions associated with the quiz
        cursor.execute(
            "SELECT QUESTION, ANSWER_A, ANSWER_B, ANSWER_C, ANSWER_D, CORRECT_ANSWER FROM QUESTIONS WHERE QUIZ_ID = ?",
            (quiz_id,))
        questions = []
        for row in cursor.fetchall():
            question_text, option_a, option_b, option_c, option_d, correct_answer = row
            questions.append({
                'question_text': question_text,
                'option_a': option_a,
                'option_b': option_b,
                'option_c': option_c,
                'option_d': option_d,
                'correct_answer': correct_answer
            })

        cursor.close()

        return render_template('quiz_editor.html', quiz_id=quiz_id, quiz_name=quiz_name, quiz_desc=quiz_desc,
                               questions=questions)
    else:
        return render_template('prohibited.html')



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
            {'option_id': 'optionA', 'option_text': answer_a},
            {'option_id': 'optionB', 'option_text': answer_b},
            {'option_id': 'optionC', 'option_text': answer_c},
            {'option_id': 'optionD', 'option_text': answer_d}
        ]
        questions.append({'id': question_id, 'question_text': question_text, 'options': options})

    cursor.close()

    # Render the template with quiz details and questions
    return render_template('take_quiz.html', quiz_id = quiz_id, quiz_name=quiz_name, quiz_desc=quiz_desc, questions=questions)





@website.route('/quiz_taking', methods=['GET', 'POST'])
def quiz_taking():
    if request.method == 'POST':
        quiz_id = request.form.get('quiz_id')

        cursor = database.conn.cursor()
        cursor.execute("SELECT * FROM questions WHERE quiz_id = ?", (quiz_id,))
        questions = cursor.fetchall()

        cursor.execute("SELECT MAX(ATTEMPT_ID) FROM ATTEMPT_HISTORY_LOG ")
        query = cursor.fetchone()
        latest_attempt_id = 0
        if query is not None:
            latest_attempt_id = query[0]

        #Creates an array of inputted answers. You don't even need this to be honest, but if you want all the answers in one array, here ya go
        inputtedAnswers = {}
        totalCorrect = 0
        totalIncorrect = 0
        cursor = database.conn.cursor()

        cursor.execute("SELECT MAX(ATTEMPT_NUMBER) FROM ATTEMPT_HISTORY_LOG WHERE EMPLOYEE_ID=? AND QUIZ_ID=?",
                       (session['id'], quiz_id))
        # curr_attempt = (0 if cursor.fetchone() is None else cursor.fetchone()[0]) + 1
        recent_attempt = cursor.fetchone()
        if recent_attempt[0] is not None:
            curr_attempt = recent_attempt[0] + 1
        else:
            curr_attempt = 1

        # Goes through each question in the quiz and checks them against the correct answer for each problem.
        for question in questions:
            question_id = question[0]
            inputAnswer = request.form.get('question_' + str(question_id))
            inputtedAnswers[question_id] = inputAnswer
            if inputAnswer == question[7]:
                #print("correct!") # This can be deleted, I was just testing it.
                totalCorrect += 1
                cursor.execute("UPDATE QUESTIONS SET NUM_CORRECT = NUM_CORRECT + 1 WHERE QUESTION_ID=?", (int(question_id),))

                # Records the submission for this question on this specific attempt into the RESULTS table
                cursor.execute('INSERT INTO RESULTS(ATTEMPT_ID,EMPLOYEE_ID,QUIZ_ID,QUESTION_ID,ANSWER,IS_CORRECT)'
                               'VALUES(?,?,?,?,?,?) ', (latest_attempt_id+1, session['id'], quiz_id,question_id,question[7],1))
            else:
                totalIncorrect += 1
                cursor.execute("UPDATE QUESTIONS SET NUM_INCORRECT = NUM_INCORRECT + 1 WHERE QUESTION_ID=?", (int(question_id),))

                # Records the submission for this question on this specific attempt into the RESULTS table
                cursor.execute('INSERT INTO RESULTS(ATTEMPT_ID,EMPLOYEE_ID,QUIZ_ID,QUESTION_ID,ANSWER,IS_CORRECT)'
                               'VALUES(?,?,?,?,?,?) ',
                               (latest_attempt_id+1, session['id'], quiz_id, question_id, question[7], 0))

        prev_attempt = (0,0,0)
        cursor.execute("SELECT MAX(ATTEMPT_NUMBER), NUM_CORRECT, NUM_INCORRECT "
                       "FROM ATTEMPT_HISTORY_LOG "
                       "WHERE EMPLOYEE_ID = ? AND QUIZ_ID = ?", (session['id'],quiz_id))
        query = cursor.fetchone()

        if query[0] is not None:
            prev_attempt = (query[0], query[1], query[2])


        cursor.execute("UPDATE QUIZZES SET TOTAL_CORRECT = TOTAL_CORRECT + ? WHERE QUIZ_ID=?", (int(totalCorrect-prev_attempt[1]), int(quiz_id),))
        cursor.execute("UPDATE QUIZZES SET TOTAL_INCORRECT = TOTAL_INCORRECT + ? WHERE QUIZ_ID=?", (int(totalIncorrect-prev_attempt[2]), int(quiz_id),))

        database.conn.commit()



        cursor.execute("INSERT INTO ATTEMPT_HISTORY_LOG(ATTEMPT_ID,EMPLOYEE_ID,QUIZ_ID,ATTEMPT_NUMBER,DATE_TIME,IS_COMPLETED,NUM_CORRECT,NUM_INCORRECT) "
                       "VALUES(?,?,?,?,?,?,?,?) ", (latest_attempt_id+1,session['id'],quiz_id,curr_attempt,datetime.datetime.now(), 1 if totalIncorrect == 0 else 0, totalCorrect, totalIncorrect,))



        # send_reports.send_report()

        database.conn.commit()





    # This redirects to the employee dashboard, I tried putting dashboard and it wouldn't let me so I did this.
    # Later this will redirect to another page where it'll display the score you got, if you get less than 100,
    # It will just contain a retry button, and if you get 100, there will be another button for returning to dashboard.
    return redirect(url_for('authenticate_user'))

@website.route('/quiz_editing', methods=['GET', 'POST'])
def quiz_editing():
    if session['role'] == 1 or session['role'] == 2:
        count = 0
        file_data = None  # Define file_data variable outside the conditional block
        # Check if the quiz name, quiz description, and material name is inputted into their text boxes.
        if request.method == 'POST' and 'quiz_name' in request.form and 'quiz_desc' in request.form and 'material_name' in request.form:
            # Retrieve data from the HTML form
            quiz_id = request.form['quiz_id']
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
            cursor.execute('UPDATE QUIZZES SET IS_DELETED=1 WHERE QUIZ_ID=?', (int(quiz_id),))
            cursor.execute('INSERT INTO QUIZZES (QUIZ_NAME, TOTAL_QUESTIONS, TOTAL_CORRECT, TOTAL_INCORRECT, IS_VISIBLE, QUIZ_DESC, IS_DELETED) VALUES (?, ?, ?, ?, ?, ?, ?)', (quiz_name, count, 0, 0, 1, quiz_desc, 0))


            #Gets the ID from the quiz that was just created to upload that into the questions that are created.
            cursor.execute('SELECT MAX(QUIZ_ID) FROM QUIZZES')
            quizID = cursor.fetchone()[0]

            cursor.execute("SELECT MAX(CHANGE_NUMBER) FROM QUIZ_HISTORY_LOG WHERE EMPLOYEE_ID=? AND QUIZ_ID=?",
                           (session['id'], quizID))
            # curr_attempt = (0 if cursor.fetchone() is None else cursor.fetchone()[0]) + 1

            recent_change = cursor.fetchone()
            curr_change = 1
            if recent_change[0] is not None:
                curr_change = recent_change[0] + 1
            else:
                curr_change = 1

            cursor.execute(
                'INSERT INTO QUIZ_HISTORY_LOG(CHANGE_ID, EMPLOYEE_ID, QUIZ_ID, CHANGE_NUMBER, DATE_TIME, ACTION_TYPE)'
                'VALUES(?,?,?,?,?,?)', (None, session['id'], quizID, curr_change, datetime.datetime.now(), 'CREATE'))

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
    else:
        render_template('prohibited.html')

@website.route('/deleteQuiz/<int:quiz_id>', methods=['GET'])
def deleteQuiz_route(quiz_id):
    cursor = database.conn.cursor()
    cursor.execute("UPDATE QUIZZES SET IS_DELETED = 1 WHERE QUIZ_ID=?", (quiz_id,))

    cursor.execute("SELECT MAX(CHANGE_NUMBER) FROM QUIZ_HISTORY_LOG WHERE EMPLOYEE_ID=? AND QUIZ_ID=?",
                   (session['id'], quiz_id))

    recent_change = cursor.fetchone()
    curr_change = 1
    if recent_change[0] is not None:
        curr_change = recent_change[0] + 1
    else:
        curr_change = 1

    cursor.execute(
        'INSERT INTO QUIZ_HISTORY_LOG(CHANGE_ID, EMPLOYEE_ID, QUIZ_ID, CHANGE_NUMBER, DATE_TIME, ACTION_TYPE)'
        'VALUES(?,?,?,?,?,?)', (None, session['id'], quiz_id, curr_change, datetime.datetime.now(), 'DELETE'))

    database.conn.commit()

    return redirect(url_for('manage_quizzes'))

@website.route('/editQuiz/<int:quiz_id>', methods=['GET'])
def editQuiz_route(quiz_id):
    cursor = database.conn.cursor()
    cursor.execute("UPDATE QUIZZES SET IS_DELETED = 1 WHERE QUIZ_ID=?", (quiz_id,))
    database.conn.commit()

    return redirect(url_for('manage_quizzes'))

