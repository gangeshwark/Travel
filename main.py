import os

import MySQLdb

from flask import Flask, request
from flask.templating import render_template


app = Flask(__name__)
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
cur = db.cursor()

class datas():
    title = "Hello"
    body = "Hello Tathagat, Neel & Tushar!"


@app.route('/')
def hello_world():
    return render_template('index.html', data=datas)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.form['username'] != '':
        string = str(request.form['username'])
        if isinstance(string, str):
            print string
    else:
        return render_template('verify.html', title="Enter a username!")
    query = """SELECT pw FROM HELLO.users WHERE username = '%s' """ % (string)
    # query = cgi.escape("select pw from users where username = %s")
    #cur.execute("""select pw from users where username = %s """, string)
    cur.execute(query)
    list1 = []
    #for row in cur.fetchall():
    #    print(row[0])
    #dic = dict[('id',row[0]),('name',row[1]),('des',row[2])]
    #    list2 = [row[0],cgi.escape(row[1])+"\n",cgi.escape(row[2])+"\n"]
    #    list1.append(list2)
    row = cur.fetchone()
    msg = 'Login Successful'
    if row == None:
        msg = "Invalid username!"
    elif request.form['password'] != row[0]:
        msg = 'Invalid password!'

    db.close()
    return render_template('verify.html', title=msg, list=list1)

if __name__ == '__main__':
    app.run()