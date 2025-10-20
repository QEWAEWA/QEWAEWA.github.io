from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/karta')
def karta():
    return render_template('karta.html')

@app.route('/lor')
def lor():
    return "Страница с лором (в разработке)"

@app.route('/ankety')
def ankety():
    return "Страница с анкетами (в разработке)"

if __name__ == '__main__':
    app.run(debug=True)