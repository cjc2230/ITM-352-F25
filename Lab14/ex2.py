from flask import Flask, render_template, request, url_for, redirect
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():   
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Here you would normally validate the username and password
        if USERS.get(username) == password:
            return redirect(url_for('success!', username=username))
        else:
            return "invalid credentials, womp womp:("
    else:
        return render_template('login.html')

@app.route('/success/<username>')
def success(username):
    return render_template('success.html', username=username)

USERS = { "cj.cornforth": "password1",
        "user2": "password2"
        }

if __name__ == '__main__':
    app.run(debug=True)