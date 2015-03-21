import os

import MySQLdb


__author__ = 'GANGESHWAR'
env = os.getenv('SERVER_SOFTWARE')
if (env and env.startswith('Google App Engine/')):
    # Connecting from App Engine
    db = MySQLdb.connect(
        unix_socket='/cloudsql/travbud2015:travbud',
        user='root')
else:
    # Connecting from an external network.
    # Make sure your network is whitelisted
    db = MySQLdb.connect(
        host='173.194.85.97',
        port=3306,
        user='root',
        passwd='travbud2015'
    )


def close():
    return db.close()


def cursor():
    return db.cursor()