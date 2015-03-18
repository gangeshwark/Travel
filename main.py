from flask import Flask, request
from flask.templating import render_template

app = Flask(__name__)
from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('main', 'static/templates'))


class datas():
    title = "Hello"
    body = "Hello Tathagat, Neel & Tushar!"


@app.route('/')
def hello_world():
    return render_template("index.html", data=datas)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = 'Hello User!'
    if request.form['username'] != "admin":
        error = "Invalid username!"
    elif request.form['password'] != "admin":
        error = 'Invalid password!'

    tem = env.get_template('verify.html')
    return tem.render(title=error)


if __name__ == '__main__':
    app.run()