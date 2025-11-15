from flask import Flask, render_template, request, redirect, url_for, session
from string import ascii_lowercase
import random
import json
import os 

app = Flask(__name__)
app.secret_key = 'a_very_secret_and_complex_key_string' # secret key for session management

# requirement 7: storage for user data
DATA_FILE = 'user_data.json'
USER_DATA = {}

def load_user_data():
    # loads user data from the json file.
    global USER_DATA
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                USER_DATA = json.load(f)
            except json.JSONDecodeError:
                USER_DATA = {}
    print(f"Loaded {len(USER_DATA)} user records.")

def save_user_data():
    # saves the current USER_DATA dictionary to the json file.
    with open(DATA_FILE, 'w') as f:
        json.dump(USER_DATA, f, indent=2) 
        print("User data saved successfully.")

# requirement 1: welcome user to home page!

@app.route('/')
def home():
    user_id = session.get('user_id')
    
    user_info = USER_DATA.get(user_id, {})
    
    username = user_info.get('username') # get username
    history = user_info.get('history', []) # get quiz history
    
    return render_template('index.html', username=username, history=history)

# requirement 1: keep track of users by name
@app.route('/set_name', methods=['POST'])
def set_name():
    global USER_DATA
    new_username = request.form['name']
    
    # use the name as the key for the user
    user_id = new_username
    
    # store the user id in the session
    session['user_id'] = user_id
    
    # create or update USER_DATA
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {'username': new_username, 'history': []}

    # save after a new user is created
    save_user_data()
    
    return redirect(url_for('quiz'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    global question_num, QUESTIONS, score 
    
    if 'user_id' not in session:
        return redirect(url_for('home'))

    # post request logic
    if request.method == 'POST':
        current_index = question_num - 1 # the just answered question
        current_text = questions[current_index][0] # question text

        correct_answer = QUESTIONS[current_text]['answer']
        explanation = QUESTIONS[current_text]['explanation']

        if(request.form.get('answer') == correct_answer):
            score += 1
            the_result = "🥳 Correct! 🥳"
            feedback_color = "green"
        else:
            the_result = "🤔 Incorrect 🤔"
            feedback_color = "red"
            
        return render_template('question_result.html', 
                               question_result = the_result, 
                               question = current_text, 
                               answer = request.form.get('answer'), 
                               correct_answer = correct_answer, 
                               explanation = explanation,
                               feedback_color = feedback_color)

    # --- GET Request Logic (Display Next Question) ---
    
    question_num += 1 
    
    if(question_num > len(questions)):
        return redirect(url_for('result'))
        
    current_index = question_num - 1

    question = questions[current_index][0]
    ordered_alternatives = random.sample(questions[current_index][1], len(questions[current_index][1]))

    return render_template('quiz.html', num=question_num, question= question, options=ordered_alternatives)

@app.route('/result') 
def result():
    global score, question_num 
    # store the result in the user's history
    user_id = session.get('user_id')
    user_info = USER_DATA.get(user_id)

    if user_info:
        user_info['history'].append({'score': score, 'total': len(questions)})
        save_user_data() # save the data to the file immediately

    template = render_template('result.html', score=score, total=len(questions))
    
    score = 0         
    question_num = 0  
    return template 

# prepare_questions function
def prepare_questions(all_questions, num_questions):
    num_questions = min(num_questions, len(all_questions))
    selected_items = random.sample(list(all_questions.items()), k=num_questions)
    processed_questions = [(q_text, q_data['options']) for q_text, q_data in selected_items]
    return processed_questions

# main quiz steps: preparing questions, running the quiz, giving feedback
NUM_QUESTIONS_PER_QUIZ = 10
question_file_path = 'questions.json'

try:
    with open(question_file_path, 'r') as f:
        QUESTIONS = json.load(f)
except FileNotFoundError:
    print(f"Error: Required file '{question_file_path}' not found.")
    QUESTIONS = {}

print(f"Loaded {len(QUESTIONS)} questions")
questions = prepare_questions(QUESTIONS, num_questions=NUM_QUESTIONS_PER_QUIZ)
print(questions)

question_num = 0  
score = 0         

if __name__ == '__main__':
    load_user_data() 
    app.run(debug=True, use_reloader=False)