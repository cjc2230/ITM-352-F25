from flask import Flask, render_template, request, redirect, url_for
import requests

url = "https://meme-api.com/gimme/wholesomememes"

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return redirect(url_for('meme'))

@app.route('/meme', methods=['GET'])
def meme():
    response = requests.get(url)    # fetch a fresh meme on each request
    data = response.json()
    meme_url = data['url']
    title = data['title']
    return render_template('meme.html', meme_url=meme_url, title=title)

if __name__ == '__main__':
    app.run(debug=True)