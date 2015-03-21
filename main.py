import os

import MySQLdb
from google.appengine.ext import blobstore

from werkzeug.http import parse_options_header

from flask import Flask, request, make_response
from flask.templating import render_template

env = os.getenv('SERVER_SOFTWARE')
if (env and env.startswith('Google App Engine/')):
    # Connecting from App Engine
    db = MySQLdb.connect(
        unix_socket='/cloudsql/gcdc2014-gangeshwark:testdb',
        user='root')
else:
    # Connecting from an external network.
    # Make sure your network is whitelisted
    db = MySQLdb.connect(
        host='173.194.251.37',
        port=3306,
        user='root')
app = Flask(__name__)


class datas():
    title = "Hello"
    body = "Hello Tathagat, Neel & Tushar!"


@app.route('/')
def hello_world():
    return render_template('index.html', data=datas)


@app.route('/login', methods=['GET', 'POST'])
def login():
    cur = db.cursor()
    # string = ''
    un = str(request.form['username'])
    pw = str(request.form['password'])
    if un == '':
        return render_template('verify.html', title="Enter a username!")
    elif pw == '':
        return render_template('verify.html', title="Enter a Password!")

    query = """SELECT pw FROM HELLO.users WHERE username = '%s' """ % (un)
    cur.execute(query)
    list1 = []
    row = cur.fetchone()
    msg = 'Login Successful'
    if row == None:
        msg = "Invalid username!"
    elif str(request.form['password']) != row[0]:
        msg = 'Invalid password!'

    db.close()
    return render_template('verify.html', title=msg, list=list1)


@app.route('/upload')
def upload():
    uploadUri = blobstore.create_upload_url('/submit')
    return render_template('upload.html', uploadUri=uploadUri)


@app.route("/submit", methods=['POST'])
def submit():
    if request.method == 'POST':
        f = request.files['file']
        header = f.headers['Content-Type']
        parsed_header = parse_options_header(header)
        blob_key = parsed_header[1]['blob-key']
        return blob_key


@app.route("/img/<bkey>")
def img(bkey):
    blob_info = blobstore.get(bkey)
    response = make_response(blob_info.open().read())
    response.headers['Content-Type'] = blob_info.content_type
    return response


if __name__ == '__main__':
    app.run()