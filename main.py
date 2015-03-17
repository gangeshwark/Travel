from flask import Flask
import jinja2
from flask.templating import render_template

app = Flask(__name__)

class datas():
    title = "Hello"
    body = "Hello Tathagat, Neel & Tushar!"

@app.route('/')
def hello_world():

    return render_template("index.html", data = datas)

if __name__ == '__main__':
    app.run()
