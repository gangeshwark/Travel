from flask import Flask, request
from flask.templating import render_template

app = Flask(__name__)
class datas():
    title = "Hello"
    body = "Hello Tathagat, Neel & Tushar!"


@app.route('/')
def hello_world():
    return render_template('index.html', data=datas)

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = 'Hello User!'
    if request.form['username'] != "admin":
        msg = "Invalid username!"
    elif request.form['password'] != "admin":
        msg = 'Invalid password!'
    return render_template('verify.html', title=msg)

if __name__ == '__main__':
    app.run()