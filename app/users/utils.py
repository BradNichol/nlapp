from app import mail
from flask_mail import Message
from flask import url_for



def send_reset_email(user):
    token = user.reset_token()
    msg = Message('Password Reset Request', sender='noreply@nutreelife.co.uk', recipients=[user.email])

    msg.body = f''' To reset your password, please visit the following link:
{url_for('users.reset_token', token=token, _external=True)}    
'''
    mail.send(msg)