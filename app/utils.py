import sqlite3
from app import mail
from flask_mail import Message
from app.models import User
from flask import url_for


# sqlite db connection
def db_connect(arg=None):
    con = sqlite3.connect('app/database.db')
    if not arg:
        con.row_factory = sqlite3.Row
        return con
    elif arg == 'update':
        return con
    else:
        return 'error'


# had problems with serializing object, both with alchemy & sqlite. 
# (data) Solution below from https://medium.com/@PyGuyCharles/python-sql-to-json-and-beyond-3e3a36d32853
# turned above solution into a function for reusability
def serialize(cur, result):
    data = [dict(zip([key[0] for key in cur.description], row)) for row in result]
    return data


def send_reset_email(user):
    token = user.reset_token()
    msg = Message('Password Reset Request', sender='noreply@nutreelife.co.uk', recipients=[user.email])

    msg.body = f''' To reset your password, please visit the following link:
{url_for('users.reset_token', token=token, _external=True)}    
'''
    mail.send(msg)