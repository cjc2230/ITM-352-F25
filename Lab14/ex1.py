from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return ("Welcome to my super awesome amazing website!")

if __name__ == '__main__':
    app.run(debug=True)