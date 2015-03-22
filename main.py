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
            return redirect(url_for('index'))

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
    id = session['logged_in']
    con = _create_connection()
    cur = con.cursor()
    query = """Select name from travel.credentials WHERE uid = %s"""%(id)
    cur.execute(query)
    row = cur.fetchone()
    return render_template('feeds.html',name = row[0])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/users',  methods=['GET'])
def users():
    db =_create_connection()
    cur = db.cursor()
    query = """SELECT uid,name FROM travel.credentials"""
    cur.execute(query)
    row = cur.fetchall()
    return render_template("users.html",users = row)

# When the user
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    db = _create_connection()
    cur = db.cursor()
    input1 = str(request.form['input'])
    print(input1)
    if input1 == 'Primary':
        email = str(request.form['email'])
        password = str(request.form['password'])
        rpassword = str(request.form['rpassword'])
        nam = str(request.form['username'])
        if password != rpassword:
            response_msg = [
            {'result': -1, 'reason': 'Passwords do not match!'}
            ]
            return jsonify(results=response_msg)
        query = """insert into travel.credentials(email,passwrd,name) VALUES ('%s','%s','%s')"""%(email,password,nam)
        try:
            cur.execute(query)
            db.commit()
        except BaseException as e:
            string = e[1]
            print(e)
            response_msg = [
                        {'result': -1, 'reason': 'Email id exists in our database.'}
                    ]
            cur.close()
            db.close()
            return jsonify(results=response_msg)
        query = """Select uid from travel.credentials where email= '%s' """ %(email)
        cur.execute(query)
        row = cur.fetchone()
        print(row)
        session['logged_in'] = row[0]
        response_msg = [
            {'result': 1, 'reason': 'success'}
        ]
        cur.close()
        db.close()
        return jsonify(results=response_msg)

    if input1 == 'Secondary':
        age = str(request.form['age'])
        sex = str(request.form['sex'])
        vist = str(request.form['visited'])
        notvist = str(request.form['notvisited'])
        query = """UPDATE travel.credentials SET credentials.img_key = '%s', age = '%s', sex = '%s' WHERE uid = '%s' ;""" %(age,age,sex,session['logged_in'])
        cur.execute(query)
        db.commit()
        response_msg = [
            {'result': 1, 'reason': 'Update complete'}
        ]
        print vist, session['logged_in']
        #query = """INSERT INTO travel.visited (uid, interest) VALUES (%s, '%s')""" %(session['logged_in'],vist)
        query = "INSERT INTO travel.visited (uid, interest) VALUES ("+str(session['logged_in'])+", '"+vist+"')"
        cur.execute(query)
        db.commit()
        #query = """INSERT INTO travel.notvisited (uid, interest) VALUES (%s , '%s')""" %(session['logged_in'],notvist)
        query = "INSERT INTO travel.notvisited (uid, interest) VALUES ("+str(session['logged_in'])+", '"+notvist+"')"
        cur.execute(query)
        db.commit()
        cur.close()
        db.close()
        response_msg = [
            {'result': 1, 'reason': 'Update complete'}
        ]
        return jsonify(results=response_msg)


@app.route('/')
def index():
    uploadUri = blobstore.create_upload_url('/signup')
    return render_template('index.html')


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
            {'result': -1, 'reason': 'inappropriate'}
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
        #return redirect(url_for('home'))
        response_msg = [
            {
                'result': 1,
                'reason': 'login successful'
            }
        ]
        return jsonify(results=response_msg)
    else:
        response_msg = [
            {'result': -1, 'reason': 'inappropriate'}
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
        query = """SELECT travel.credentials.img_key FROM travel.credentials WHERE uid = %s """ % (session['logged_in'])
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

@app.route('/planmytravel', methods=['POST', 'GET'])
def planmytravel():
    return render_template('planmytravel.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    db =_create_connection()
    cur = db.cursor()
    receiver = request.args.get('userid')
    if receiver == None:
        return redirect(url_for('home'))
    else:
        query = """SELECT uid,name,sex,age,alias FROM travel.credentials WHERE uid = %s """ % receiver
        cur.execute(query)
        row = cur.fetchall()
        if row == None:
            return redirect(url_for('home'))
            db.close()
        list = []
        for k in row:
            for p in k:
                list.append(p)
        query = """SELECT interest FROM travel.visited WHERE uid = %s """ % receiver
        cur.execute(query)
        row = cur.fetchall()
        print("I have traveled")
        list1 = []
        for k in row:
            list1.append(k[0])
        query = """SELECT interest FROM travel.notvisited WHERE uid = %s """ % receiver
        cur.execute(query)
        crow = cur.fetchall()
        list2 = []
        for k in crow:
            list2.append(k[0])
        print(list1)
        print(list2)
        return render_template('profile.html',name=list[1],sex=list[2],age=list[3],alias=list[4],visited=list1,notvisited=list2)

class profile:
    name = "Rahul"
    age = "55"
    sex = "Female"
    location = "New York"

@app.route('/plantrip', methods=['GET', 'POST'])
def plantrip():
    print("something")


if __name__ == '__main__':
    app.run(debug=True)