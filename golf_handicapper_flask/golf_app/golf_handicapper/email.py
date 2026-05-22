from flask import render_template, url_for
from flask_mail import Message
from . import mail


def send_activation_email(user, token):
    link = url_for('auth.activate', token=token, email=user.email, _external=True)
    msg  = Message('The Golf Handicapper – Activate Your Account',
                   recipients=[user.email])
    msg.html = render_template('email/account_activation.html', user=user, link=link)
    msg.body = render_template('email/account_activation.txt',  user=user, link=link)
    mail.send(msg)


def send_password_reset_email(user, token):
    link = url_for('auth.password_reset', token=token, email=user.email, _external=True)
    msg  = Message('The Golf Handicapper – Password Reset',
                   recipients=[user.email])
    msg.html = render_template('email/password_reset.html', user=user, link=link)
    msg.body = render_template('email/password_reset.txt',  user=user, link=link)
    mail.send(msg)
