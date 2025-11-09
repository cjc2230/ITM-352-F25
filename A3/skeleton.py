from flask import Flask, session, request, redirect, url_for, render_template_string
import json, random, os
from string import ascii_lowercase

app = Flask(__name__)
app.secret_key = os.urandom(24)

# load questions (same JSON file your CLI app used)
with open("questions2.json", "r") as f:
    QUESTIONS = json.load(f)

NUM_QUESTIONS = 10

start_tpl = """
<!doctype html>
<title>Quiz</title>
<h1>Quick Quiz</h1>
<p>You'll get {{n}} questions.</p>
<form action="{{ url_for('start') }}" method="post">
  <button type="submit">Start Quiz</button>
</form>
"""

question_tpl = """
<!doctype html>
<title>Question {{ idx + 1 }}</title>
<h2>Question {{ idx + 1 }} / {{ total }}</h2>
<p><strong>{{ q['question'] }}</strong></p>
<form method="post" action="{{ url_for('answer') }}">
  {% for opt in q['options'] %}
    <div><label><input type="radio" name="choice" value="{{ opt|e }}" required> {{ opt }}</label></div>
  {% endfor %}
  <button type="submit">Submit</button>
</form>
"""

answer_tpl = """
<!doctype html>
<title>Answer</title>
<h2>{{ result }}</h2>
<p><strong>Question:</strong> {{ q['question'] }}</p>
<p><strong>Your answer:</strong> {{ given }}</p>
<p><strong>Correct answer:</strong> {{ correct }}</p>
{% if q['explanation'] %}
  <p><em>Explanation:</em> {{ q['explanation'] }}</p>
{% endif %}
<form action="{{ next_url }}" method="get">
  <button type="submit">{{ button_text }}</button>
</form>
"""

result_tpl = """
<!doctype html>
<title>Result</title>
<h1>Quiz complete</h1>
<p>You scored {{ score }} / {{ total }}.</p>
<form action="{{ url_for('start') }}" method="post">
  <button type="submit">Play again</button>
</form>
"""

def prepare_questions(questions, num):
    num = min(num, len(questions))
    chosen = random.sample(list(questions.items()), num)
    out = []
    for q, info in chosen:
        opts = info["options"][:]
        random.shuffle(opts)
        out.append({
            "question": q,
            "options": opts,
            "answer": info["answer"],
            "explanation": info.get("explanation", "")
        })
    return out

@app.route("/", methods=["GET"])
def index():
    return render_template_string(start_tpl, n=NUM_QUESTIONS)

@app.route("/start", methods=["POST", "GET"])
def start():
    session["quiz"] = prepare_questions(QUESTIONS, NUM_QUESTIONS)
    session["idx"] = 0
    session["correct"] = 0
    return redirect(url_for("question"))

@app.route("/question", methods=["GET"])
def question():
    quiz = session.get("quiz")
    idx = session.get("idx", 0)
    if not quiz or idx >= len(quiz):
        return redirect(url_for("result"))
    q = quiz[idx]
    return render_template_string(question_tpl, q=q, idx=idx, total=len(quiz))

@app.route("/answer", methods=["POST"])
def answer():
    choice = request.form.get("choice")
    quiz = session.get("quiz")
    idx = session.get("idx", 0)
    if not quiz or idx >= len(quiz) or not choice:
        return redirect(url_for("index"))
    q = quiz[idx]
    correct = q["answer"]
    given = choice
    is_correct = (given == correct)
    if is_correct:
        session["correct"] = session.get("correct", 0) + 1
        result = "Correct!"
    else:
        result = "Incorrect."
    # advance index
    session["idx"] = idx + 1
    # decide next URL
    if session["idx"] >= len(quiz):
        next_url = url_for("result")
        button_text = "See results"
    else:
        next_url = url_for("question")
        button_text = "Next question"
    return render_template_string(answer_tpl, result=result, q=q, given=given, correct=correct, next_url=next_url, button_text=button_text)

@app.route("/result", methods=["GET"])
def result():
    score = session.get("correct", 0)
    total = len(session.get("quiz", []))
    # append to score_history.json
    fname = "score_history.json"
    history = []
    if os.path.exists(fname):
        try:
            with open(fname, "r") as fh:
                history = json.load(fh)
        except Exception:
            history = []
    history.append({"score": score, "total": total})
    with open(fname, "w") as fh:
        json.dump(history, fh, indent=2)
    return render_template_string(result_tpl, score=score, total=total)

if __name__ == "__main__":
    app.run(debug=True)