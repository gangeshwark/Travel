import os
from functools import wraps

import MySQLdb
from google.appengine.ext import blobstore

from flask import jsonify
from flask import session, url_for, flash
from werkzeug.http import parse_options_header
from flask import Flask, request, make_response, redirect
from flask.templating import render_template


app = Flask(__name__)
app.secret_key = 'my precious'
app.config['SESSION_TYPE'] = 'filesystem'
# SESSION CHECKIN FOR EVERY AUTHORIZED PAGE
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first')
            return redirect(url_for('hello_world'))

    return wrap


class datas():
    title = "Hello"
    body = "Hello Tathagat, Neel & Tushar!"


def _create_connection():
    if (os.getenv('SERVER_SOFTWARE') and
            os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
        return MySQLdb.connect(
            unix_socket='/cloudsql/travbud2015:travbud',
            user='root')
    else:
        return MySQLdb.connect(
            host='173.194.85.97',
            port=3306,
            user='root',
            passwd='travbud2015'
        )


# When the user signs up for the first time
@app.route('/home')
@login_required
def home():
    return render_template('upload.html')


# When the user
@app.route('/signup', methods=['POST'])
def signup_1():
    input1 = str(request.form['input'])
    if input1 == 'Primary':
        username = str(request.form['email'])
        password = str(request.form['password'])
        rpassword = str(request.form['rpassword'])
        name = str(request.form['name'])
        age = str(request.form['age'])
        sex = str(request.form['sex'])
        if (password != rpassword):
            return

    if input1 == 'Secondary':
        return 1


@app.route('/sign', methods=['POST'])
def signup_2():
    return

@app.route('/')
def home1():
    return render_template('index.html', data=datas)


@app.route('/login', methods=['POST'])
def login():
    state = 0
    conn = _create_connection()
    cur = conn.cursor()
    # string = ''
    un = str(request.form['username'])
    pw = str(request.form['password'])
    if un == '' or pw == '':
        response_msg = [
            {'error': -1, 'reason': 'inappropriate'}
        ]
        return jsonify(results=response_msg)
    query = """SELECT passwrd,uid FROM travel.credentials WHERE email = '%s' ;""" % (un)
    cur.execute(query)
    list1 = []
    row = cur.fetchone()
    print row

    if row != None:
        if pw == row[0]:
            state = 1
    cur.close()
    conn.close()
    if state == 1:
        session['logged_in'] = row[1]
        return redirect(url_for('home'))
    else:
        response_msg = [
            {
                'error': -1,
                'reason': 'Invalid Username/Password'
            }
        ]
        return jsonify(results=response_msg)


@app.route('/upload')
@login_required
def upload1():
    uploadUri = blobstore.create_upload_url('/submit')
    return render_template('upload.html', uploadUri=uploadUri)


@app.route("/submit", methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        f = request.files['file']
        header = f.headers['Content-Type']
        parsed_header = parse_options_header(header)
        blob_key = parsed_header[1]['blob-key']
        print blob_key, session['logged_in']

        conn = _create_connection()
        cur = conn.cursor()

        query = """UPDATE travel.credentials SET credentials.img_key = '%s' WHERE credentials.uid = %s ;""" % (
        blob_key, session['logged_in'])
        print(query)
        cur.execute(query)
        conn.commit()

        query = """SELECT credentials.img_key FROM travel.credentials WHERE uid = %s """ % (session['logged_in'])
        cur.execute(query)
        row = cur.fetchone()

        conn.close()
        cur.close()
        return redirect("/view/" + row[0], code=302)


@app.route("/view/<bkey>")
def img(bkey):
    blob_info = blobstore.get(bkey)
    response = make_response(blob_info.open().read())
    response.headers['Content-Type'] = blob_info.content_type
    return response

if __name__ == '__main__':
    app.run(debug=True)