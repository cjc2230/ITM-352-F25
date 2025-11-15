from flask import Flask, render_template, request, redirect, url_for, session
from string import ascii_lowercase
import random
import json

app = Flask(__name__)
# *** ADD SECRET KEY ***
app.secret_key = 'a_very_secret_and_complex_key_string' 
# **********************

@app.route('/')
def home():
    username = session.get('username')
    history = session.get('history', []) 
    # *** FIX 1: Pass the session variables to the template ***
    return render_template('index.html', username=username, history=history)

@app.route('/set_name', methods=['POST'])
def set_name():
    # Save the user's name from the form into the session
    session['username'] = request.form['name']
    # Initialize history if it doesn't exist
    if 'history' not in session:
        session['history'] = []
    return redirect(url_for('quiz'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    global question_num, QUESTIONS, score 

    # *** FIX 2: REMOVED INCORRECT HISTORY LOGIC FROM HERE ***

    # --- POST Request Logic (User Submitting an Answer) ---
    if request.method == 'POST':
        # The question that was just answered is at index question_num - 1
        current_q_index = question_num - 1
        current_q_text = questions[current_q_index][0]
        
        # Look up correct data from the master QUESTIONS dictionary
        correct_answer = QUESTIONS[current_q_text]['answer']
        q_explanation = QUESTIONS[current_q_text]['explanation']
        
        # Process the answer
        if(request.form.get('answer') == correct_answer):
            score += 1
            the_result = "🥳 Correct! 🥳"
            feedback_color = "green"
        else:
            the_result = "🤔 Incorrect 🤔"
            feedback_color = "red"

        # Display the result (feedback page)
        return render_template('question_result.html', 
                               question_result = the_result, 
                               question = current_q_text, 
                               answer = request.form.get('answer'), 
                               correct_answer = correct_answer, # Pass for display
                               explanation = q_explanation) # Pass for display
    
    # --- GET Request Logic (Display Next Question) ---
    
    question_num += 1 
    
    # quiz over? then redirect to the result page
    if(question_num > len(questions)):
        return redirect(url_for('result'))
        
    current_q_index = question_num - 1
    
    # Get the question and answer options
    a_question = questions[current_q_index][0]
    ordered_alternatives = random.sample(questions[current_q_index][1], k=len(questions[current_q_index][1]))

    return render_template('quiz.html', num=question_num, question= a_question, options=ordered_alternatives)

@app.route('/result') 
def result():
    global score, question_num 
    if 'history' not in session:
        session['history'] = []
        
    # 2. RECORD THE SCORE
    # Record the final score before resetting global variables
    session['history'].append({'score': score, 'total': len(questions)})
    
    # 3. RENDER FINAL PAGE
    # get the result template (final summary)
    template = render_template('result.html', score=score, total=len(questions))
    
    # 4. RESET GLOBALS (Only used for the next quiz)
    score = 0         
    question_num = 0  
    
    # Flask sessions are typically saved automatically, but this ensures it.
    session.modified = True 
    
    return template

# Functions for main processing steps
def prepare_questions(all_questions, num_questions):
    num_questions = min(num_questions, len(all_questions))
    
    selected_items = random.sample(list(all_questions.items()), k=num_questions)
    
    processed_questions = [(q_text, q_data['options']) for q_text, q_data in selected_items]
    
    return processed_questions

# Main quiz steps: preparing questions, running the quiz, giving feedback
# Read in and load the file of quiz questions
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

# Run the application
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)